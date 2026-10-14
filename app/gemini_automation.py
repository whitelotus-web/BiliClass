"""Gemini's visible web UI: isolated Chrome, durable sends and PPTX downloads.

No private endpoints, cookies, tokens or API keys are read. Authentication is
performed by the teacher in ordinary Chrome before the saved profile is checked.
"""

import hashlib
import json
import re
import time
from pathlib import Path
from threading import Event
from urllib.parse import urlsplit

from . import browser_automation as chrome
from .browser_accounts import profile_lock
from .browser_services import conversation_url as provider_url
from .chatgpt_handoff import inspect_returned_deck, load_request
from .conversion_progress import emit_progress
from .document_limits import MAX_POWERPOINT_BYTES

HOME = "https://gemini.google.com/app"
COMPOSER = 'rich-textarea .ql-editor[contenteditable="true"], [contenteditable="true"][role="textbox"], textarea[aria-label]'
PROFILE = ('[aria-label*="Google Account"], [aria-label*="Tài khoản Google"], '
           '[aria-label*="Cuenta de Google"], a[href*="accounts.google.com/SignOutOptions"]')
SEND = ('button[aria-label="Send message"], button[aria-label="Gửi tin nhắn"], '
        'button[aria-label="Submit"], button[aria-label="Gửi"], button.send-button')
STOP = 'button[aria-label="Stop response"], button[aria-label="Dừng phản hồi"], button[aria-label="Stop generating"]'
MODEL_PICKER = 'button[data-test-id="bard-mode-menu-button"], button.gds-mode-switch-button, button[aria-label*="mode picker"], button[aria-label*="model picker"], button[aria-label*="mô hình"]'
USERS = 'user-query, [data-test-id="user-query"]'
ANSWERS = 'model-response, [data-test-id="model-response"]'
BrowserProblem = chrome.BrowserProblem
check_cancel = chrome.check_cancel
write_record = chrome.write_record
open_context = chrome.open_context
visible = chrome.visible


def conversation_url(url):
    return provider_url(url, "gemini")


def read_record(folder, account_id):
    return chrome.read_record(folder, account_id, "gemini")


def navigate(page, url, cancel):
    from playwright.sync_api import TimeoutError

    check_cancel(cancel)
    if url != HOME and not conversation_url(url):
        raise BrowserProblem("record", "Địa chỉ phiên Gemini không hợp lệ.")
    try:
        page.goto(url, wait_until="commit", timeout=20000)
    except TimeoutError as exc:
        if urlsplit(page.url).hostname != "gemini.google.com":
            raise BrowserProblem("network", "Chưa tải được Gemini. Phiên đăng nhập vẫn được giữ.") from exc
    check_cancel(cancel)


def page_problem(page):
    if urlsplit(page.url).hostname == "accounts.google.com":
        raise BrowserProblem("login", "Đăng nhập hoặc xác minh tài khoản Google trong Browser AI để dùng Gemini.")
    login = page.get_by_role("link", name=re.compile(r"^(?:Sign in|Đăng nhập)$", re.I))
    login_button = page.get_by_role("button", name=re.compile(r"^(?:Sign in|Đăng nhập)$", re.I))
    if not visible(page, PROFILE) and any(x.is_visible() for x in login.all() + login_button.all()):
        raise BrowserProblem("login", "Chưa đăng nhập Gemini. Mở tài khoản trong Browser AI.")
    for notice in page.locator('[role="alert"], [role="status"], .error-container, .error-message').all():
        if not notice.is_visible() or notice.locator('xpath=ancestor::user-query | ancestor::model-response').count():
            continue
        text = notice.inner_text()
        if re.search(r"(?:reached|exceeded|usage|daily).{0,45}limit|hết (?:lượt|hạn mức)|đã (?:đạt|vượt).{0,30}giới hạn", text, re.I):
            raise BrowserProblem("limit", "Gemini báo hết lượt. Bài và phiên được giữ để tiếp tục khi hạn mức được cấp lại.")
        if re.search(r"(?:verify|confirm).{0,20}(?:human|you)|xác minh.{0,20}(?:bạn|con người)", text, re.I):
            raise BrowserProblem("verification", "Gemini cần xác minh trực tiếp. Mở tài khoản trong Browser AI để hoàn tất.")
        if re.search(r"something went wrong|connection interrupted|network error|đã xảy ra lỗi|lỗi (?:mạng|kết nối)", text, re.I):
            raise BrowserProblem("network", "Gemini tạm gián đoạn. Tool giữ lượt đã gửi để tiếp tục, không gửi trùng.")


def require_account(page, cancel, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        if urlsplit(page.url).hostname == "gemini.google.com" and visible(page, PROFILE) and visible(page, COMPOSER):
            return
        page.wait_for_timeout(250)
    raise BrowserProblem("interface", "Chưa xác nhận được phiên Gemini. Mở tài khoản để kiểm tra đăng nhập hoặc quyền truy cập.")


def inspect_session(page, cancel):
    limited = False
    try:
        require_account(page, cancel)
    except BrowserProblem as exc:
        if exc.code != 'limit' or not visible(page, PROFILE) or not visible(page, COMPOSER):
            raise
        limited = True
    profile = visible(page, PROFILE)
    label = (profile.get_attribute("aria-label") or profile.get_attribute("title") or profile.inner_text())
    email = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", label)
    name = re.sub(r"Google Account:|Tài khoản Google:|\([^)]*@[^)]*\)", "", label).strip()
    plan = "unknown"
    for element in page.locator('[data-test-id="account-plan"], [data-test-id="current-plan"], [data-testid="current-plan"]').all():
        if element.is_visible() and not element.locator('xpath=ancestor::user-query | ancestor::model-response').count():
            text = element.inner_text().strip()
            if re.fullmatch(r'(?:Google AI )?(Free|Pro|Ultra)', text, re.I):
                plan = text.split()[-1].casefold()
                break
    return {"ready": True, "name": name[:100], "email": email.group(0) if email else "", "plan": plan,
            "quota_limited": limited}


def login(account, root, cancel, progress, url=HOME, *, finish=None, awaiting_confirmation=None, timeout=600):
    from playwright.sync_api import sync_playwright

    from .chrome_session import PlainChromeLogin

    finish = finish or Event()
    target = url if conversation_url(url) else HOME
    with profile_lock(root, account["id"]):
        check_cancel(cancel)
        browser = PlainChromeLogin(account, target)
        try:
            if awaiting_confirmation:
                awaiting_confirmation(True)
            progress("Đăng nhập Google trong Chrome riêng. Khi vào được Gemini, đóng cửa sổ hoặc bấm Kiểm tra và lưu.")
            deadline = time.monotonic() + timeout
            while browser.running() and not finish.is_set():
                check_cancel(cancel)
                if time.monotonic() >= deadline:
                    raise BrowserProblem("timeout", "Chưa xác nhận đăng nhập Gemini. Profile được giữ để mở lại.")
                cancel.wait(.2)
            check_cancel(cancel)
            browser.finish()
        finally:
            browser.close()
            if awaiting_confirmation:
                awaiting_confirmation(False)
        with sync_playwright() as playwright:
            context = open_context(playwright, account, background=True, cancel=cancel)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                navigate(page, target, cancel)
                return inspect_session(page, cancel)
            finally:
                context.close()


def check_session(account, root, cancel, progress):
    from playwright.sync_api import sync_playwright

    with profile_lock(root, account["id"]), sync_playwright() as playwright:
        context = open_context(playwright, account, background=True, cancel=cancel)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            navigate(page, HOME, cancel)
            return inspect_session(page, cancel)
        finally:
            context.close()


def select_model(page):
    selector = visible(page, MODEL_PICKER)
    if not selector:
        raise BrowserProblem("model", "Chưa tìm được bộ chọn model Gemini. Chưa gửi bài; mở tài khoản để kiểm tra giao diện.")
    selector.click()
    choices = []
    deadline = time.monotonic() + 3
    while not choices and time.monotonic() < deadline:
        for item in page.locator('[role="menu"] [role="menuitem"], [role="menu"] [role="menuitemradio"], [role="listbox"] [role="option"], [role="menu"] button, .bard-mode-menu button').all():
            if not item.is_visible() or not item.is_enabled() or item.get_attribute("aria-disabled") == "true" or item.get_attribute('data-disabled') in {'', 'true'}:
                continue
            text = item.inner_text().strip()
            if re.search(r"upgrade|nâng cấp|subscribe|đăng ký", text, re.I):
                continue
            rank = 4 if re.search(r"deep think", text, re.I) else 3 if re.search(r"\bpro\b", text, re.I) else 2 if re.search(r"thinking|suy nghĩ", text, re.I) else 1 if re.search(r"fast|nhanh", text, re.I) else 0
            if rank:
                version = re.search(r"(?:Gemini\s*)?(\d+)\.(\d+)", text, re.I)
                choices.append(((rank, int(version[1]) if version else 0, int(version[2]) if version else 0), item, text))
        if not choices:
            page.wait_for_timeout(100)
    if choices:
        _, item, text = max(choices, key=lambda row: row[0])
        item.click()
        page.wait_for_timeout(150)
        active = visible(page, MODEL_PICKER)
        if active and _normalized(text.splitlines()[0]).casefold() in _normalized(active.inner_text()).casefold():
            return text.splitlines()[0][:160]
        from .browser_reasoning import selected
        if not active:
            raise BrowserProblem("model", "Gemini không còn hiển thị model sau khi chọn. Chưa gửi bài.")
        active.click()
        confirmed = any(x.is_visible() and selected(x) and x.inner_text().strip() == text
                        for x in page.locator('[role="menuitem"], [role="menuitemradio"], [role="option"]').all())
        page.keyboard.press("Escape")
        if confirmed:
            return text.splitlines()[0][:160]
        raise BrowserProblem("model", "Gemini chưa xác nhận model cao nhất đã chọn. Chưa gửi bài.")
    page.keyboard.press("Escape")
    raise BrowserProblem("model", "Chưa đọc được model Gemini được phép dùng. Chưa gửi bài; mở tài khoản để kiểm tra.")


def _normalized(text):
    return re.sub(r"\s+", " ", text or "").strip()


def _digest(text):
    return hashlib.sha256(_normalized(text).encode("utf-8")).hexdigest()


def _query_text(node):
    child = node.locator('.query-text, [data-test-id="query-text"]')
    return (child.first if child.count() else node).inner_text() or ""


def _history(page):
    links = []
    for item in page.locator('a[href]').all():
        href = item.get_attribute("href") or ""
        href = "https://gemini.google.com" + href if href.startswith('/') else href
        if conversation_url(href) and href not in links:
            links.append(href)
    return links[:30]


def _receipt(page, folder, record, wanted, cancel, timeout=25):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        if conversation_url(page.url):
            queries = page.locator(USERS)
            if queries.count() > record.get("user_before", 0) and _digest(_query_text(queries.last)) == wanted:
                record.update(state="waiting", url=page.url, error="")
                write_record(folder, record)
                return True
        page.wait_for_timeout(250)
    return False


def _wait_upload(page, files, cancel, progress):
    deadline = time.monotonic() + max(45, sum(p.stat().st_size for p in files) / (128 * 1024))
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        chips = page.locator('file-preview, .file-preview, .file-preview-container, [data-test-id="attachment"], [data-test-id="file-preview"]')
        labels = [chip.inner_text() + " " + (chip.get_attribute("aria-label") or "") for chip in chips.all()
                  if chip.is_visible() and not chip.locator('xpath=ancestor::user-query | ancestor::model-response').count()]
        if all(any(p.name in label for label in labels) for p in files) and not visible(page, '.upload-progress, [aria-label="Uploading"]'):
            return
        page.wait_for_timeout(250)
    raise BrowserProblem("upload", "Gemini chưa nhận đủ tài liệu. Chưa gửi yêu cầu thiếu tệp.")


def submit(page, folder, record, prompt, cancel, *, files=(), progress=None):
    from playwright.sync_api import TimeoutError

    check_cancel(cancel)
    page_problem(page)
    if record.get("require_highest_model"):
        from .browser_model_policy import prepare_models
        record.update(prepare_models(page, "gemini"))
        write_record(folder, record)
    field = visible(page, COMPOSER)
    if not field:
        raise BrowserProblem("interface", "Chưa tìm được ô nhập yêu cầu của Gemini.")
    field.fill(prompt)
    if files:
        if len(files) > 10 or any(p.stat().st_size > 100 * 1024**2 for p in files):
            raise BrowserProblem("attachments", "Gemini nhận tối đa 10 tệp, mỗi tệp tối đa 100 MB trong một lượt.")
        chips = page.locator('file-preview, .file-preview, .file-preview-container, [data-test-id="attachment"], [data-test-id="file-preview"]')
        for chip in chips.all()[::-1]:
            if not chip.is_visible() or chip.locator('xpath=ancestor::user-query | ancestor::model-response').count():
                continue
            remove = chip.get_by_role('button', name=re.compile(r"Remove|Delete|Xóa|Gỡ", re.I))
            if not any(x.is_visible() and x.is_enabled() for x in remove.all()):
                raise BrowserProblem("upload", "Ô soạn thảo Gemini còn tệp cũ chưa xóa được. Chưa gửi bài để tránh dùng sai nguồn.")
            remove.first.click()
        upload = chrome.upload_field(page, files)
        if upload:
            upload.set_input_files([str(p) for p in files])
        else:
            add = page.get_by_role("button", name=re.compile(r"^(?:Add files|Thêm tệp|Upload files|Upload & tools|Tải tệp lên)$", re.I))
            if not any(x.is_visible() for x in add.all()):
                raise BrowserProblem("interface", "Chưa tìm được nút tải tài liệu của Gemini.")
            add.first.click()
            upload = chrome.upload_field(page, files)
            if upload:
                upload.set_input_files([str(p) for p in files])
            else:
                item = page.get_by_role("menuitem", name=re.compile(r"Upload files|Tải tệp lên", re.I))
                with page.expect_file_chooser(timeout=10000) as chooser:
                    item.first.click()
                chooser.value.set_files([str(p) for p in files])
        _wait_upload(page, files, cancel, progress)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        send = visible(page, SEND)
        if send and send.is_enabled() and not visible(page, STOP):
            break
        page.wait_for_timeout(200)
    else:
        raise BrowserProblem("interface", "Gemini chưa sẵn sàng gửi yêu cầu; tài liệu chưa được gửi.")
    field = visible(page, COMPOSER)
    if not field or _digest(field.input_value() if field.evaluate("e => e.tagName === 'TEXTAREA'") else field.inner_text()) != _digest(prompt):
        raise BrowserProblem("interface", "Nội dung yêu cầu đã thay đổi. Chưa gửi bài.")
    answers = page.locator(ANSWERS)
    intent = {"account_id": record["account_id"], "browser_service": "gemini", "prompt": prompt,
              "sha256": _digest(prompt), "history_before": _history(page), "url_before": page.url if conversation_url(page.url) else ""}
    intent_path = Path(folder) / "gemini-send-intent.json"
    temporary = intent_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(intent, ensure_ascii=False), encoding="utf-8")
    temporary.replace(intent_path)
    record.update(state="submitting", browser_service="gemini", send_sha256=intent["sha256"],
                  user_before=page.locator(USERS).count(), assistant_before=answers.count(),
                  assistant_ids_before=[x.get_attribute("id") for x in answers.all() if re.fullmatch(r"[A-Za-z0-9_-]{1,160}", x.get_attribute("id") or "")])
    write_record(folder, record)
    try:
        send.click(timeout=10000)
    except TimeoutError as exc:
        raise BrowserProblem("receipt", "Đang xác minh lượt gửi Gemini; không bấm gửi lại khi chưa rõ kết quả.") from exc
    if not _receipt(page, folder, record, intent["sha256"], cancel):
        raise BrowserProblem("receipt", "Chưa xác nhận được lượt gửi Gemini. Tool giữ yêu cầu để tìm lại, không gửi trùng.")


def recover_submission(page, folder, record, cancel):
    try:
        intent = json.loads((Path(folder) / "gemini-send-intent.json").read_text(encoding="utf-8"))
        if (intent["account_id"] != record["account_id"] or intent["browser_service"] != "gemini"
                or intent["sha256"] != record.get("send_sha256") or _digest(intent["prompt"]) != intent["sha256"]):
            raise ValueError("Invalid receipt")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise BrowserProblem("receipt", "Bản ghi lượt gửi Gemini chưa đủ để khôi phục an toàn. Không tự gửi lại bài.") from exc
    if record.get("url") or intent.get("url_before"):
        urls = [record.get("url") or intent["url_before"]]
    else:
        navigate(page, HOME, cancel)
        require_account(page, cancel)
        urls = [u for u in _history(page) if u not in intent.get("history_before", [])]
    for url in urls:
        navigate(page, url, cancel)
        require_account(page, cancel)
        if _receipt(page, folder, record, intent["sha256"], cancel, timeout=5):
            return
    raise BrowserProblem("receipt", "Chưa tìm lại được lượt gửi Gemini đã xác nhận. Bài được giữ, không tự gửi thêm.")


def _latest(page, record):
    nodes = page.locator(ANSWERS)
    ids = record.get("assistant_ids_before", [])
    if ids:
        fresh = [x for x in nodes.all() if x.get_attribute("id") and x.get_attribute("id") not in ids]
        return fresh[-1] if fresh else None
    return nodes.last if nodes.count() > record.get("assistant_before", 0) else None


def _trusted_result_url(url):
    parsed = urlsplit(url)
    if url.startswith("blob:https://gemini.google.com/"):
        return True
    host = parsed.hostname or ""
    return (parsed.scheme == "https" and not parsed.username and not parsed.password and not parsed.port
            and (host in {"gemini.google.com", "docs.google.com", "drive.google.com", "storage.googleapis.com"}
                 or host.endswith(".googleusercontent.com") or host.endswith(".usercontent.google.com")))


def result_link(page, record):
    reply = _latest(page, record)
    if reply is None:
        return None
    for link in reply.locator('a[href]').all()[::-1]:
        href = link.get_attribute("href") or ""
        if href.startswith('/'):
            href = "https://gemini.google.com" + href
        label = link.inner_text() + " " + (link.get_attribute("download") or "")
        if _trusted_result_url(href) and (".pptx" in (label + href).casefold() or re.match(r"https://docs\.google\.com/presentation/d/", href)):
            return link
    for control in reply.get_by_role("button", name=re.compile(r"\.pptx\b|Export to Slides|Xuất sang (?:Google )?Trang trình bày", re.I)).all()[::-1]:
        if control.is_visible() and control.is_enabled():
            return control
    # Canvas must belong to this latest reply, never an arbitrary earlier deck.
    artifact = reply.get_by_role("button", name=re.compile(r"Open|Mở", re.I))
    if any(x.is_visible() for x in artifact.all()) and reply.locator('canvas-artifact, [data-test-id="canvas-artifact"], .artifact-card').count():
        artifact.first.click()
        export = page.get_by_role("button", name=re.compile(r"Export to Slides|Xuất sang (?:Google )?Trang trình bày", re.I))
        if any(x.is_visible() for x in export.all()):
            return export.first
        menu = page.get_by_role("button", name=re.compile(r"Share & export|Chia sẻ và xuất", re.I))
        if any(x.is_visible() for x in menu.all()):
            menu.first.click()
            export = page.get_by_role("menuitem", name=re.compile(r"Export to Slides|Xuất sang (?:Google )?Trang trình bày", re.I))
            if any(x.is_visible() for x in export.all()):
                return export.first
    return None


def wait_result(page, folder, record, cancel, progress, timeout=900):
    deadline = time.monotonic() + timeout
    last_text, stable_since, last_progress = "", time.monotonic(), 0
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        if not visible(page, STOP):
            entry = result_link(page, record)
            if entry:
                return entry
            reply = _latest(page, record)
            text = reply.inner_text() if reply is not None else ""
            if text != last_text:
                last_text, stable_since = text, time.monotonic()
            if text and time.monotonic() - stable_since > 8:
                if not record["followups"]:
                    record["followups"] = 1
                    write_record(folder, record)
                    submit(page, folder, record, "Hoàn tất bài giảng theo yêu cầu trước và xuất tệp PowerPoint .pptx chỉnh sửa được để tải xuống. Có thể tạo bản trình bày trong Canvas và dùng Export to Slides. Không chỉ đưa dàn ý, HTML hoặc mã Python; không tạo hình thay nội dung nguồn.", cancel)
                    last_text, stable_since = "", time.monotonic()
                else:
                    raise BrowserProblem("no_file", "Gemini chưa trả PowerPoint tải được. Bài và cuộc trò chuyện đã được giữ; cần kiểm tra quyền tạo/xuất tệp của tài khoản.")
        if time.monotonic() - last_progress > 20:
            emit_progress(progress, "waiting", "Đang biên soạn bài giảng…")
            last_progress = time.monotonic()
        page.wait_for_timeout(400)
    raise BrowserProblem("timeout", "Gemini chưa hoàn tất bài trong thời gian chờ. Lượt đã gửi được giữ để tiếp tục.")


def receive_download(page, entry, cancel, timeout=60, progress=None):
    context = page.context
    downloads, seen = [], set(context.pages)
    hooked = []
    def on_download(download):
        downloads.append(download)

    def watch(tab):
        tab.on("download", on_download)
        hooked.append(tab)

    watch(page)
    context.on("page", watch)
    try:
        entry.click(timeout=10000)
        deadline, exported = time.monotonic() + timeout, False
        while time.monotonic() < deadline:
            check_cancel(cancel)
            if downloads:
                return downloads[-1]
            for tab in context.pages:
                if tab.is_closed():
                    continue
                if (tab == page or tab not in seen) and re.match(r"https://docs\.google\.com/presentation/(?:u/\d+/)?d/", tab.url) and not exported:
                    file_menu = visible(tab, '#docs-file-menu') or tab.get_by_role("menuitem", name=re.compile(r"^(File|Tệp)$", re.I)).first
                    if file_menu.count() and file_menu.is_visible():
                        file_menu.click()
                        menu = tab.get_by_role("menuitem", name=re.compile(r"^Download|^Tải xuống", re.I))
                        menu.first.hover()
                        item = tab.get_by_role("menuitem", name=re.compile(r"Microsoft PowerPoint.*pptx|PowerPoint.*pptx", re.I))
                        item.first.click()
                        exported = True
                elif tab == page or tab not in seen:
                    if urlsplit(tab.url).hostname not in {"gemini.google.com", "docs.google.com", "drive.google.com"}:
                        continue
                    button = tab.get_by_role("button", name=re.compile(r"^(?:Download|Download file|Tải xuống|Tải tệp)$", re.I))
                    if any(x.is_visible() and x.is_enabled() for x in button.all()):
                        button.first.click()
            page.wait_for_timeout(250)
        raise BrowserProblem("download", "Chưa tải được PowerPoint từ Gemini/Google Slides. Phiên và bài đã được giữ.")
    finally:
        context.remove_listener("page", watch)
        for tab in hooked:
            tab.remove_listener("download", on_download)
            if tab != page and tab not in seen and not tab.is_closed():
                tab.close()


def convert(account, root, folder, cancel, progress, *, timeout=900, observed=None):
    from playwright.sync_api import sync_playwright

    if account.get("service") != "gemini":
        raise BrowserProblem("account", "Chọn đúng profile Gemini cho yêu cầu này.")
    request = load_request(folder)
    if request["config"].get("browser_service", "chatgpt") != "gemini":
        raise BrowserProblem("account", "Yêu cầu đã lưu thuộc dịch vụ khác; không gửi sang Gemini.")
    folder = Path(folder)
    record = read_record(folder, account["id"])
    record["require_highest_model"] = request["config"].get("require_highest_model", False)
    target = folder / "bai-giang-song-ngu.pptx"
    if record["state"] == "completed" and target.is_file():
        if hashlib.sha256(target.read_bytes()).hexdigest() != record.get("sha256"):
            raise BrowserProblem("result", "PowerPoint đã lưu bị thay đổi; nhận lại đúng kết quả trước khi dùng.")
        inspect_returned_deck(target)
        return {"path": str(target), "url": record["url"], "cached": True}
    files = [folder / name for name in request["attachments"]]
    if any(p.parent.resolve() != folder.resolve() or not p.is_file() or p.stat().st_size > 100 * 1024**2 for p in files):
        raise BrowserProblem("attachments", "Tài liệu Gemini bị thiếu, thay đổi hoặc vượt 100 MB.")
    write_record(folder, record)
    try:
        with profile_lock(root, account["id"]), sync_playwright() as playwright:
            context = open_context(playwright, account, background=True, cancel=cancel)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(10000)
                emit_progress(progress, "session", "Đang chuẩn bị phiên chuyển đổi…")
                if record["state"] == "submitting":
                    recover_submission(page, folder, record, cancel)
                else:
                    navigate(page, record["url"] or HOME, cancel)
                    require_account(page, cancel)
                identity = inspect_session(page, cancel)
                if record["state"] == "prepared":
                    if conversation_url(page.url):
                        navigate(page, HOME, cancel)
                        require_account(page, cancel)
                    if conversation_url(page.url):
                        raise BrowserProblem("interface", "Gemini còn mở cuộc trò chuyện cũ. Chưa gửi bài mới để tránh lẫn tài liệu.")
                    record.update(plan=identity["plan"])
                    if not record["require_highest_model"]:
                        record.update(model=select_model(page), reasoning="Theo quyền trên Gemini")
                    write_record(folder, record)
                    emit_progress(progress, "upload", "Đang chuẩn bị tài liệu cho bài giảng…")
                    submit(page, folder, record, request["prompt"], cancel, files=files, progress=progress)
                if observed:
                    observed(account["id"], identity["plan"], record.get("model", ""))
                entry = wait_result(page, folder, record, cancel, progress, timeout)
                emit_progress(progress, "download", "Đang nhận bài giảng kết quả…")
                download = receive_download(page, entry, cancel, progress=progress)
                pending = folder / "ket-qua-chua-kiem-tra.pptx"
                if Path(download.suggested_filename).suffix.casefold() != '.pptx' or not download.path() or Path(download.path()).stat().st_size > MAX_POWERPOINT_BYTES:
                    raise BrowserProblem("download", "Gemini trả tệp chưa phải PowerPoint hợp lệ; không báo hoàn tất.")
                download.save_as(str(pending))
                inspect_returned_deck(pending)
                if request["config"].get("quality_review_version") == 1:
                    from .slide_refinement import refine
                    refine(page, folder, record, request, pending, cancel, progress, timeout)
                pending.replace(target)
                record.update(state="completed", stage="completed", error="", sha256=hashlib.sha256(target.read_bytes()).hexdigest())
                write_record(folder, record)
                return {"path": str(target), "url": record["url"], "cached": False}
            finally:
                context.close()
    except Exception as exc:
        code = exc.code if isinstance(exc, BrowserProblem) else "browser"
        record.update(error=code, failure_type=type(exc).__name__)
        write_record(folder, record)
        if isinstance(exc, (BrowserProblem, ValueError)):
            raise
        raise BrowserProblem(code, "Phiên Gemini tạm gián đoạn. Tool giữ bài và lượt đã gửi để tiếp tục.") from exc
