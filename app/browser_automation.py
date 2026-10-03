"""Experimental ChatGPT web UI adapter. No API, stealth or challenge bypass.

Selectors are isolated here. Only explicit app jobs upload local attachments.
Each job records the conversation before waiting; retries never blindly resend.
"""

import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urlsplit

from .browser_accounts import profile_lock
from .chatgpt_handoff import inspect_returned_deck, load_request
from .importers import MAX_BYTES

CHATGPT = "https://chatgpt.com/"
COMPOSER = '#prompt-textarea, textarea[data-testid="prompt-textarea"], [contenteditable="true"][data-testid="composer"]'
PROFILE = '[data-testid="accounts-profile-button"], [data-testid="profile-button"], button[aria-label="Open profile menu"]'
SEND = '[data-testid="send-button"], button[aria-label="Send prompt"], button[aria-label="Gửi lời nhắc"], button[aria-label="Send message"]'
STOP = '[data-testid="stop-button"], button[aria-label="Stop generating"], button[aria-label="Dừng tạo"]'
ASSISTANT = '[data-message-author-role="assistant"]'
EXPORT_PROMPT = (
    "Hãy hoàn tất tệp bai-giang-song-ngu.pptx chỉnh sửa được theo yêu cầu đã gửi và cung cấp liên kết tải .pptx "
    "trong câu trả lời. Không chỉ đưa dàn ý hoặc đường dẫn nội bộ dạng văn bản. "
    "Nếu không thể tạo tệp trong phiên này, hãy nói rõ giới hạn."
)


class BrowserProblem(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def check_cancel(cancel):
    if cancel.is_set():
        raise BrowserProblem("cancelled", "Đã dừng Browser AI. Yêu cầu đã gửi trên ChatGPT có thể vẫn đang xử lý.")


def conversation_url(value):
    parsed = urlsplit(value)
    return (parsed.scheme == "https" and parsed.netloc == "chatgpt.com" and not parsed.query
            and bool(re.fullmatch(r"/c/[a-zA-Z0-9-]+", parsed.path)))


def visible(page, selector):
    for locator in page.locator(selector).all():
        if locator.is_visible():
            return locator
    return None


def page_problem(page):
    title = page.title().casefold()
    if ("just a moment" in title or "verify you are human" in title
            or visible(page, 'iframe[src*="challenges.cloudflare.com"], #challenge-running, #challenge-stage')):
        raise BrowserProblem("verification", "ChatGPT yêu cầu xác minh browser. Mở Đăng nhập trong Browser AI và xử lý trực tiếp.")
    if urlsplit(page.url).hostname in {"auth.openai.com", "auth0.openai.com"}:
        raise BrowserProblem("login", "Phiên ChatGPT hết hạn. Đăng nhập lại tài khoản trong Browser AI.")
    if visible(page, '[data-testid="login-button"], [data-testid="login-button-header"]'):
        raise BrowserProblem("login", "Chưa đăng nhập ChatGPT. Mở Cài đặt → Browser AI → Đăng nhập.")


def require_account(page, cancel, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        if visible(page, PROFILE) and visible(page, COMPOSER):
            return
        page.wait_for_timeout(250)
    raise BrowserProblem("interface", "Chưa xác nhận được tài khoản ChatGPT hoặc giao diện web đã đổi. Mở browser để kiểm tra.")


def open_context(playwright, account, *, headless):
    try:
        return playwright.chromium.launch_persistent_context(
            account["profile"], channel=account["channel"], headless=headless,
            accept_downloads=True, viewport={"width": 1360, "height": 900},
            timeout=30000, chromium_sandbox=True,
        )
    except Exception as exc:
        # Never show driver logs; they may include session URLs or profile details.
        raise BrowserProblem("browser", "Chưa mở được browser riêng. Cài/cập nhật Microsoft Edge và đóng phiên đang dùng tài khoản này.") from exc


def login(account, root, cancel, progress, url=CHATGPT, *, auto_close=True):
    from playwright.sync_api import Error, sync_playwright

    from .browser_capabilities import detect_plan

    with profile_lock(root, account["id"]), sync_playwright() as playwright:
        context = open_context(playwright, account, headless=False)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url if conversation_url(url) else CHATGPT, wait_until="domcontentloaded", timeout=45000)
            progress("Đăng nhập trên web. Tool sẽ tự lưu phiên khi đăng nhập thành công.")
            ready_since = None
            while not cancel.is_set():
                if page.is_closed():
                    return {"ready": False, "message": "Đã đóng browser. Có thể mở lại để kiểm tra phiên."}
                try:
                    signed_in = (urlsplit(page.url).hostname == "chatgpt.com"
                                 and visible(page, PROFILE) and visible(page, COMPOSER))
                    if auto_close and signed_in:
                        ready_since = ready_since or time.monotonic()
                        if time.monotonic() - ready_since >= 1:
                            plan = detect_plan(page, PROFILE)
                            return {"ready": True, "plan": plan, "message": "Đã đăng nhập và tự lưu phiên ChatGPT."}
                    else:
                        ready_since = None
                except Error:
                    # OAuth navigation can temporarily replace the page's DOM.
                    ready_since = None
                page.wait_for_timeout(250)
            return {"ready": False, "message": "Đã đóng phiên browser."}
        except Error as exc:
            raise BrowserProblem("browser", "Browser đăng nhập đã đóng hoặc mất kết nối. Mở lại để tiếp tục.") from exc
        finally:
            try:
                context.close()
            except Error:
                pass


def write_record(folder, record):
    target = Path(folder) / "browser-job.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)


def read_record(folder, account_id):
    target = Path(folder) / "browser-job.json"
    if not target.exists():
        return {"account_id": account_id, "state": "prepared", "url": "", "followups": 0}
    record = json.loads(target.read_text(encoding="utf-8"))
    if record.get("account_id") != account_id:
        raise BrowserProblem("account", "Yêu cầu này dùng tài khoản khác. Chọn lại tài khoản đã gửi để tiếp tục.")
    if (record.get("state") not in {"prepared", "submitting", "waiting", "completed"}
            or type(record.get("followups")) is not int or not 0 <= record["followups"] <= 1):
        raise BrowserProblem("record", "Trạng thái yêu cầu Browser AI không hợp lệ.")
    if record.get("url") and not conversation_url(record["url"]):
        raise BrowserProblem("record", "Địa chỉ cuộc trò chuyện trong yêu cầu không hợp lệ.")
    return record


def wait_upload(page, files, cancel, timeout=120):
    field = page.locator('input[type="file"]').first
    if not field.count():
        attach = visible(page, '#upload-file-btn, [data-testid="composer-plus-btn"], button[aria-label="Add files and more"]')
        if not attach:
            raise BrowserProblem("interface", "Chưa tìm được nút đính kèm trên web ChatGPT. Giao diện có thể đã đổi.")
        attach.click(timeout=5000)
        upload = page.get_by_text(re.compile(r"^(Upload from computer|Add photos & files|Tải lên từ máy tính|Thêm ảnh và tệp)$", re.I)).first
        with page.expect_file_chooser(timeout=5000) as chooser:
            upload.click(timeout=5000)
        chooser.value.set_files([str(p) for p in files])
    else:
        field.set_input_files([str(p) for p in files], timeout=10000)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        # Require an actual rendered attachment for every requested file.
        attached = all(page.get_by_text(p.name, exact=True).count() for p in files)
        sending = visible(page, SEND)
        loading = visible(page, '[data-testid="file-upload-progress"], [role="progressbar"], [data-testid="attachment-loading"]')
        if attached and sending and sending.is_enabled() and not loading:
            return
        page.wait_for_timeout(300)
    raise BrowserProblem("upload", "Tệp chưa tải lên xong hoặc web không nhận tệp. Không gửi prompt thiếu tài liệu.")


def fill_prompt(page, prompt):
    field = visible(page, COMPOSER)
    if not field:
        raise BrowserProblem("interface", "Chưa tìm được ô prompt của ChatGPT.")
    field.fill(prompt, timeout=10000)


def submit(page, folder, record, prompt, cancel, *, files=()):
    fill_prompt(page, prompt)
    if files:
        wait_upload(page, files, cancel)
    check_cancel(cancel)
    sender = visible(page, SEND)
    if not sender or not sender.is_enabled():
        raise BrowserProblem("interface", "Nút Gửi của ChatGPT chưa sẵn sàng.")
    # Persist BEFORE click: a crash or unknown response must not trigger a duplicate send.
    record["state"] = "submitting"
    write_record(folder, record)
    sender.click(timeout=10000)
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        if conversation_url(page.url):
            record.update(state="waiting", url=page.url)
            write_record(folder, record)
            return
        page.wait_for_timeout(200)
    raise BrowserProblem("submission", "Có thể prompt đã gửi nhưng chưa xác nhận được cuộc trò chuyện. Kiểm tra browser; app không tự gửi lại.")


def result_link(page):
    # Only files in assistant messages; never source attachments, sidebar or arbitrary links.
    for anchor in page.locator(ASSISTANT + ' a[href]').all()[::-1]:
        label = (anchor.inner_text() + " " + (anchor.get_attribute("download") or "")).casefold()
        href = anchor.get_attribute("href") or ""
        if ".pptx" not in label and ".pptx" not in urlsplit(href).path.casefold():
            continue
        parsed = urlsplit(href)
        if (href.startswith(("sandbox:/mnt/data/", "/backend-api/files/", "blob:https://chatgpt.com/"))
                or parsed.scheme == "https" and (parsed.hostname == "chatgpt.com"
                or (parsed.hostname or "").endswith(".oaiusercontent.com"))):
            return anchor
    return None


def wait_result(page, folder, record, cancel, progress, timeout=900):
    deadline = time.monotonic() + timeout
    last_progress = 0
    last_text, stable_since = "", time.monotonic()
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        generating = visible(page, STOP)
        link = result_link(page)
        if link and not generating:
            return link
        messages = page.locator(ASSISTANT)
        if messages.count() and not generating:
            text = messages.last.inner_text()
            if text != last_text:
                last_text, stable_since = text, time.monotonic()
            if re.search(r"(usage limit|reached.*limit|too many requests|hạn mức|đạt giới hạn|try again later)", text, re.I):
                raise BrowserProblem("limit", "ChatGPT báo giới hạn lượt dùng. Yêu cầu được giữ lại; tiếp tục khi tài khoản dùng được.")
            if text.strip() and not link and time.monotonic() - stable_since > 4:
                if record.get("followups", 0) == 0:
                    # One follow-up only, with its count stored before submitting.
                    record["followups"] = 1
                    write_record(folder, record)
                    progress("ChatGPT chưa đưa liên kết PPTX; đang yêu cầu xuất tệp trong cùng cuộc trò chuyện…")
                    submit(page, folder, record, EXPORT_PROMPT, cancel)
                    last_progress = time.monotonic()
                    last_text, stable_since = "", time.monotonic()
                elif time.monotonic() - stable_since > 15:
                    raise BrowserProblem("no_file", "ChatGPT chưa trả file PowerPoint. Mở cuộc trò chuyện để kiểm tra khả năng tạo tệp của tài khoản.")
        if time.monotonic() - last_progress > 20:
            progress("Đang chờ ChatGPT tạo PowerPoint; bạn có thể dừng và tiếp tục cùng yêu cầu…")
            last_progress = time.monotonic()
        page.wait_for_timeout(500)
    raise BrowserProblem("timeout", "Chưa nhận PowerPoint trong thời gian chờ. Yêu cầu đã được giữ để tiếp tục, không gửi lại prompt.")


def convert(account, root, request_folder, cancel, progress, *, timeout=900, observed=None):
    with profile_lock(root, account["id"]):
        return _convert_locked(account, request_folder, cancel, progress, timeout=timeout, observed=observed)


def _convert_locked(account, request_folder, cancel, progress, *, timeout, observed):
    from playwright.sync_api import Error, sync_playwright

    from .browser_capabilities import detect_plan, select_best_model

    request = load_request(request_folder)
    folder = Path(request["folder"])
    record = read_record(folder, account["id"])
    target = folder / "bai-giang-song-ngu.pptx"
    if record["state"] == "completed" and target.is_file():
        if target.stat().st_size > MAX_BYTES or record.get("sha256") != hashlib.sha256(target.read_bytes()).hexdigest():
            raise BrowserProblem("result", "PowerPoint đã tải bị thay đổi. Nhận lại kết quả từ cuộc trò chuyện trước khi dùng.")
        inspect_returned_deck(target)
        return {"path": str(target), "url": record["url"]}
    files = [folder / name for name in request["attachments"]]
    if any(p.parent != folder or not p.is_file() or p.stat().st_size > MAX_BYTES for p in files):
        raise BrowserProblem("attachments", "Tài liệu hoặc mẫu đã thiếu/thay đổi. Chuẩn bị gói mới trước khi gửi.")
    write_record(folder, record)
    try:
        with sync_playwright() as playwright:
            progress("Đang mở phiên ChatGPT chạy ngầm…")
            context = open_context(playwright, account, headless=True)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(10000)
                page.goto(record["url"] or CHATGPT, wait_until="domcontentloaded", timeout=45000)
                require_account(page, cancel)
                plan = detect_plan(page, PROFILE)
                if record["state"] == "prepared":
                    model = select_best_model(page)
                    record.update(plan=plan, model=model)
                    write_record(folder, record)
                    progress(f"Model đang dùng: {model} · quyền truy cập theo web ChatGPT.")
                if observed:
                    observed(account["id"], plan, record.get("model", ""))
                if record["state"] == "prepared":
                    progress("Đang đính kèm tài liệu và gửi prompt đã cấu hình…")
                    submit(page, folder, record, request["prompt"], cancel, files=files)
                elif not record["url"]:
                    raise BrowserProblem("submission", "Chưa rõ yêu cầu trước đã gửi hay chưa. Kiểm tra browser; app không gửi trùng.")
                link = wait_result(page, folder, record, cancel, progress, timeout)
                progress("Đang tải và kiểm tra PowerPoint kết quả…")
                with page.expect_download(timeout=45000) as event:
                    link.click(timeout=10000)
                download = event.value
                if Path(download.suggested_filename).suffix.casefold() != ".pptx":
                    raise BrowserProblem("download", "Tệp web trả về không phải PowerPoint .pptx.")
                downloaded = download.path()
                if not downloaded or Path(downloaded).stat().st_size > MAX_BYTES:
                    raise BrowserProblem("download", "PowerPoint tải về bị lỗi hoặc vượt 50 MB.")
                pending = folder / "ket-qua-chua-kiem-tra.pptx"
                download.save_as(str(pending))
                inspect_returned_deck(pending)
                pending.replace(target)
                record.update(state="completed", error="", sha256=hashlib.sha256(target.read_bytes()).hexdigest())
                write_record(folder, record)
                return {"path": str(target), "url": record["url"]}
            finally:
                try:
                    context.close()
                except Error:
                    pass
    except Exception as exc:
        code = exc.code if isinstance(exc, BrowserProblem) else "browser"
        record.update(error=code)
        # Keep the last durable send state and conversation URL for safe resume.
        write_record(folder, record)
        if isinstance(exc, (BrowserProblem, ValueError)):
            raise
        raise BrowserProblem("browser", "Browser mất kết nối hoặc giao diện ChatGPT đã đổi. Yêu cầu được giữ lại để kiểm tra/tiếp tục.") from exc
