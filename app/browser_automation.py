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
from .browser_health import retry_delay
from .chatgpt_handoff import inspect_returned_deck, load_request
from .document_limits import MAX_POWERPOINT_BYTES, document_limit

CHATGPT = "https://chatgpt.com/"
COMPOSER = '#prompt-textarea, textarea[data-testid="prompt-textarea"], [contenteditable="true"][data-testid="composer"]'
PROFILE = '[data-testid="accounts-profile-button"], [data-testid="profile-button"], button[aria-label="Open profile menu"]'
SEND = '[data-testid="send-button"], button[aria-label="Send prompt"], button[aria-label="Gửi lời nhắc"], button[aria-label="Send message"]'
STOP = '[data-testid="stop-button"], button[aria-label="Stop generating"], button[aria-label="Dừng tạo"]'
ASSISTANT = '[data-message-author-role="assistant"]'
USER = '[data-message-author-role="user"]'
LOGIN = '[data-testid="login-button"], [data-testid="login-button-header"]'
VERIFICATION_MESSAGE = (
    "ChatGPT yêu cầu xác minh Cloudflare. Phiên và bài đang làm đã được giữ. "
    "Mở lại phiên để tự xác minh; nếu browser thường cũng bị lặp, cần kiểm tra truy cập ChatGPT trước."
)
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


def verification_required(page):
    title = page.title().casefold()
    return bool("just a moment" in title or "verify you are human" in title
                or visible(page, 'iframe[src*="challenges.cloudflare.com"], #challenge-running, #challenge-stage'))


def page_problem(page):
    if verification_required(page):
        raise BrowserProblem("verification", VERIFICATION_MESSAGE)
    authentication_problem(page)
    if urlsplit(page.url).hostname in {"auth.openai.com", "auth0.openai.com"}:
        raise BrowserProblem("login", "Phiên ChatGPT hết hạn. Đăng nhập lại tài khoản trong Browser AI.")
    if visible(page, LOGIN):
        raise BrowserProblem("login", "Chưa đăng nhập ChatGPT. Mở Cài đặt → Browser AI → Đăng nhập.")
    # Quota notices belong to web controls, not the teacher's lesson text.
    for notice in page.locator('[role="alert"], [data-testid="toast"], [data-testid="rate-limit-message"]').all():
        if (notice.is_visible() and not notice.locator('xpath=ancestor-or-self::*[@data-message-author-role]').count()
                and re.search(r"usage limit|(?:you(?:'ve| have) )?reached (?:your|the) .{0,40}limit|"
                              r"too many requests|đã (?:đạt|hết).{0,30}(?:giới hạn|hạn mức)|"
                              r"hết (?:lượt|hạn mức)", notice.inner_text(), re.I)):
            delay = retry_delay(notice.inner_text())
            hint = f" Có thể thử lại sau {delay} giây theo thông báo web." if delay else ""
            raise BrowserProblem("limit", "ChatGPT báo giới hạn lượt dùng. Bài được giữ lại để tiếp tục khi tài khoản dùng được." + hint)


def authentication_problem(page):
    """Recognize the actual full-page error, never lesson text or tokens."""
    if (urlsplit(page.url).hostname not in {"chatgpt.com", "auth.openai.com", "auth0.openai.com"}
            or visible(page, COMPOSER)):
        return
    heading = page.get_by_role("heading", name=re.compile(r"Oops,? an error occurred!?|Authentication Error", re.I))
    if any(item.is_visible() for item in heading.all()):
        error = page.get_by_text(re.compile(r"Route Error.*(?:400|Invalid content type)|Invalid content type", re.I))
        if any(item.is_visible() for item in error.all()):
            raise BrowserProblem("auth_response", "Trang đăng nhập ChatGPT trả lỗi 400 ‘Invalid content type’. Chưa lưu được kết nối; thử đăng nhập lại trong Chrome bình thường của BiliClass.")


def navigate(page, url, cancel):
    """Wait for the main document, then let readiness checks watch the controls.

    Do not retry a navigation automatically: it could restart sign-in or a
    human verification. A document-load timeout may still have a usable page.
    """
    from playwright.sync_api import TimeoutError

    check_cancel(cancel)
    try:
        page.goto(url, wait_until="commit", timeout=20000)
    except TimeoutError as exc:
        check_cancel(cancel)
        if urlsplit(page.url).hostname not in {"chatgpt.com", "auth.openai.com", "auth0.openai.com"}:
            raise BrowserProblem("network", "Chưa tải được ChatGPT. Kiểm tra mạng rồi mở lại; phiên đăng nhập được giữ.") from exc
    check_cancel(cancel)


def require_account(page, cancel, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        if visible(page, PROFILE) and visible(page, COMPOSER):
            return
        page.wait_for_timeout(250)
    raise BrowserProblem("interface", "Chưa xác nhận được tài khoản ChatGPT hoặc giao diện web đã đổi. Mở browser để kiểm tra.")


def open_context(playwright, account, *, background, cancel=None):
    from .chrome_session import open_chrome

    if cancel:
        check_cancel(cancel)
    try:
        return open_chrome(playwright, account, background=background, cancel=cancel)
    except Exception as exc:
        from .chrome_session import ChromeSessionError

        if cancel:
            check_cancel(cancel)
        if isinstance(exc, ChromeSessionError):
            raise BrowserProblem(exc.code, str(exc)) from exc
        # Never show driver logs; they may include session URLs or profile details.
        raise BrowserProblem("browser", "Chưa mở được Chrome riêng. Cài/cập nhật Google Chrome và đóng phiên đang dùng tài khoản này.") from exc


def signed_in(page):
    return bool(urlsplit(page.url).hostname == "chatgpt.com" and visible(page, PROFILE)
                and visible(page, COMPOSER) and not visible(page, LOGIN))


def login_page(context, previous):
    """Follow the ChatGPT tab when login returns in a new tab/window."""
    pages = [p for p in context.pages if not p.is_closed()]
    for page in reversed(pages):
        if urlsplit(page.url).hostname == "chatgpt.com" and signed_in(page):
            return page
    if not previous.is_closed():
        return previous
    return pages[-1] if pages else None


def login_observed(account, root, cancel, progress, url=CHATGPT, *, auto_close=True, timeout=600, verification_timeout=None):
    from playwright.sync_api import Error, sync_playwright

    from .browser_capabilities import detect_account

    with profile_lock(root, account["id"]), sync_playwright() as playwright:
        context = open_context(playwright, account, background=False, cancel=cancel)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            try:
                navigate(page, url if conversation_url(url) else CHATGPT, cancel)
                progress("Đăng nhập trên web. Tool sẽ tự lưu phiên khi đăng nhập thành công.")
            except BrowserProblem as exc:
                if exc.code != "network":
                    raise
                # A slow first document is not a failed sign-in. Leave the
                # native window available; never restart a pending auth flow.
                progress("ChatGPT đang tải chậm trong Chrome. Giữ cửa sổ mở hoặc kiểm tra truy cập tại đó; tool vẫn chờ đăng nhập.")
            ready_since = None
            verification_since = None
            identity = None
            deadline = time.monotonic() + timeout
            while not cancel.is_set() and time.monotonic() < deadline:
                try:
                    page = login_page(context, page)
                    if page is None:
                        return {"ready": False, "message": "Đã đóng Chrome. Có thể mở lại để kiểm tra phiên."}
                    if verification_required(page):
                        ready_since = None
                        if verification_since is None:
                            verification_since = time.monotonic()
                            progress("Đang chờ bạn xác minh trên ChatGPT trong Chrome. Giữ cửa sổ này mở để hoàn tất; có thể bấm Hủy trong tool.")
                        if verification_timeout is not None and time.monotonic() - verification_since >= verification_timeout:
                            raise BrowserProblem("verification", VERIFICATION_MESSAGE)
                        page.wait_for_timeout(250)
                        continue
                    authentication_problem(page)
                    verification_since = None
                    if auto_close and signed_in(page):
                        ready_since = ready_since or time.monotonic()
                        if time.monotonic() - ready_since >= 1:
                            identity = detect_account(page, PROFILE)
                            break
                    else:
                        ready_since = None
                except Error:
                    # OAuth navigation can temporarily replace the page's DOM.
                    ready_since = None
                if page and not page.is_closed():
                    page.wait_for_timeout(250)
            if identity is not None:
                progress("Đã đăng nhập trên Chrome. Đang kiểm tra phiên đã lưu có mở lại được…")
                context.close()
                check_cancel(cancel)
                context = open_context(playwright, account, background=True, cancel=cancel)
                page = context.pages[0] if context.pages else context.new_page()
                navigate(page, url if conversation_url(url) else CHATGPT, cancel)
                require_account(page, cancel)
                restored = detect_account(page, PROFILE)
                if identity.get("email") and restored.get("email") and identity["email"] != restored["email"]:
                    raise BrowserProblem("login", "Tài khoản Chrome đã thay đổi. Đăng nhập lại đúng tài khoản trong Browser AI.")
                return {"ready": True, **restored, "message": "Đã kiểm tra và lưu phiên Chrome. Có thể chuyển đổi bài giảng."}
            if not cancel.is_set():
                if verification_since is not None and verification_required(page):
                    raise BrowserProblem("verification", VERIFICATION_MESSAGE)
                raise BrowserProblem("timeout", "Hết thời gian chờ đăng nhập. Bấm Đăng nhập để mở lại phiên web.")
            return {"ready": False, "message": "Đã đóng phiên browser."}
        except Error as exc:
            raise BrowserProblem("browser", "Browser đăng nhập đã đóng hoặc mất kết nối. Mở lại để tiếp tục.") from exc
        finally:
            try:
                context.close()
            except Error:
                pass


def login(account, root, cancel, progress, url=CHATGPT, *, finish=None, awaiting_confirmation=None, timeout=600):
    """Let the human authenticate before attaching any browser controller."""
    from threading import Event

    from .chrome_session import PlainChromeLogin

    finish = finish or Event()
    target = url if conversation_url(url) else CHATGPT
    with profile_lock(root, account["id"]):
        check_cancel(cancel)
        browser = PlainChromeLogin(account, target)
        try:
            if awaiting_confirmation:
                awaiting_confirmation(True)
            progress("Đăng nhập trực tiếp trong Chrome. Khi đã vào ChatGPT, bấm ‘Kiểm tra và lưu’ tại BiliClass hoặc đóng cửa sổ Chrome riêng.")
            deadline = time.monotonic() + timeout
            while browser.running() and not finish.is_set():
                check_cancel(cancel)
                if time.monotonic() >= deadline:
                    raise BrowserProblem("timeout", "Chưa xác nhận đăng nhập trong thời gian chờ. Hồ sơ Chrome được giữ; mở lại để tiếp tục.")
                cancel.wait(.2)
            check_cancel(cancel)
            browser.finish()
        finally:
            browser.close()
            if awaiting_confirmation:
                awaiting_confirmation(False)
        check_cancel(cancel)
        progress("Đang kiểm tra tài khoản từ phiên Chrome đã lưu…")
        from playwright.sync_api import Error, sync_playwright

        with sync_playwright() as playwright:
            context = open_context(playwright, account, background=True, cancel=cancel)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                navigate(page, target, cancel)
                return inspect_session(page, cancel)
            except Error as exc:
                raise BrowserProblem("browser", "Chưa kiểm tra được phiên Chrome đã lưu. Thử đăng nhập lại trong Browser AI.") from exc
            finally:
                context.close()


def check_session(account, root, cancel, progress):
    """Read the saved session's visible controls; never upload or send a chat."""
    from playwright.sync_api import sync_playwright

    with profile_lock(root, account["id"]), sync_playwright() as playwright:
        context = open_context(playwright, account, background=True, cancel=cancel)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            navigate(page, CHATGPT, cancel)
            return inspect_session(page, cancel)
        finally:
            context.close()


def inspect_session(page, cancel):
    from .browser_capabilities import detect_account

    limited = False
    retry_after = 0
    try:
        require_account(page, cancel)
    except BrowserProblem as exc:
        if exc.code != "limit" or not signed_in(page):
            raise
        limited = True
        retry_after = retry_delay(str(exc))
    return {"ready": True, "quota_limited": limited, "retry_after_seconds": retry_after,
            **detect_account(page, PROFILE, details=True)}


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
    for key in ("assistant_before", "user_before"):
        if key in record and (type(record[key]) is not int or record[key] < 0):
            raise BrowserProblem("record", "Trạng thái câu trả lời Browser AI không hợp lệ.")
    return record


def upload_field(page, files):
    """Choose a file input that accepts this batch, rather than the camera input."""
    import mimetypes

    choices = []
    for field in page.locator('input[type="file"]').all():
        if not field.is_enabled() or len(files) > 1 and field.get_attribute("multiple") is None:
            continue
        accepted = [a.strip().casefold() for a in (field.get_attribute("accept") or "").split(",") if a.strip()]
        if accepted and not all(any(
                rule == p.suffix.casefold() or rule == (mimetypes.guess_type(p.name)[0] or "").casefold()
                or rule.endswith("/*") and (mimetypes.guess_type(p.name)[0] or "").casefold().startswith(rule[:-1])
                for rule in accepted) for p in files):
            continue
        choices.append((bool(accepted), field))
    return min(choices, key=lambda choice: choice[0])[1] if choices else None


def attachment_scope(page):
    field = visible(page, COMPOSER)
    form = field.locator('xpath=ancestor::form[1]') if field else None
    return form if form is not None and form.count() else page


def file_label(path):
    # ChatGPT's file library can rename another upload to "name(2).pptx".
    return re.escape(path.stem) + r"(?:\s*\(\d+\))?" + re.escape(path.suffix)


def attachment_present(scope, path):
    pattern = re.compile("^" + file_label(path) + "$", re.I)
    candidates = [*scope.get_by_text(pattern).all(), *scope.get_by_label(pattern).all(),
                  *scope.get_by_title(pattern).all()]
    return any(node.is_visible() and not node.locator('xpath=ancestor-or-self::*[@data-message-author-role]').count()
               for node in candidates)


def clear_draft_attachments(page, files, cancel):
    scope = attachment_scope(page)
    names = "|".join(file_label(path) for path in files)
    pattern = re.compile(r"^(?:Remove file\s+\d+:\s*|Xóa tệp\s+\d+:\s*)(?:" + names + ")$", re.I)
    for _ in range(20):
        check_cancel(cancel)
        remove = scope.get_by_role("button", name=pattern)
        found = next((node for node in remove.all() if node.is_visible()
                      and not node.locator('xpath=ancestor-or-self::*[@data-message-author-role]').count()), None)
        if found is None:
            return
        # Remove only previous app-named attachments in the unsent composer.
        # This does not delete files from the user's library or source disk.
        found.click(timeout=5000)
    raise BrowserProblem("upload", "Chưa làm sạch được tệp đính kèm của lần thử trước. Chưa gửi bài.")


def wait_upload(page, files, cancel, timeout=180):
    from playwright.sync_api import TimeoutError

    check_cancel(cancel)
    clear_draft_attachments(page, files, cancel)
    field = upload_field(page, files)
    try:
        if field is None:
            attach = visible(page, '#upload-file-btn, [data-testid="composer-plus-btn"], button[aria-label="Add files and more"]')
            if not attach:
                raise BrowserProblem("interface", "Chưa tìm được nút đính kèm trên web ChatGPT. Giao diện có thể đã đổi.")
            attach.click(timeout=5000)
            upload = page.get_by_text(re.compile(r"^(Upload from computer|Add photos & files|Tải lên từ máy tính|Thêm ảnh và tệp)$", re.I)).first
            with page.expect_file_chooser(timeout=10000) as chooser:
                upload.click(timeout=5000)
            chooser.value.set_files([str(p) for p in files], timeout=30000)
        else:
            field.set_input_files([str(p) for p in files], timeout=30000)
    except TimeoutError:
        # Chrome can set the files but time out awaiting the input event (seen
        # with a real 16 MB PPTX). Never set them a second time in this page:
        # continue observing actual rendered attachments before any send.
        check_cancel(cancel)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        # Require an actual rendered attachment for every requested file.
        attached = all(attachment_present(attachment_scope(page), p) for p in files)
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
    field = visible(page, COMPOSER)
    entered = (field.inner_text() if field and field.get_attribute("contenteditable") == "true"
               else field.input_value() if field else "")
    # ProseMirror can render paragraph breaks as two newlines. Compare all
    # non-whitespace content; a changed/missing word still prevents sending.
    if re.sub(r"\s+", " ", entered).strip() != re.sub(r"\s+", " ", prompt).strip():
        raise BrowserProblem("interface", "Ô prompt đã thay đổi trong lúc tải trang/tệp. Chưa gửi; bấm Tiếp tục để thử lại.")
    sender = visible(page, SEND)
    if not sender or not sender.is_enabled():
        raise BrowserProblem("interface", "Nút Gửi của ChatGPT chưa sẵn sàng.")
    # Persist BEFORE click: a crash or unknown response must not trigger a duplicate send.
    previous_url = page.url
    record.update(state="submitting", assistant_before=page.locator(ASSISTANT).count(),
                  user_before=page.locator(USER).count())
    write_record(folder, record)
    sender.click(timeout=10000)
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        # A follow-up already has a conversation URL. Confirm a new message
        # instead of mistaking that old URL for acknowledgement of this send.
        acknowledged = (page.url != previous_url or page.locator(USER).count() > record["user_before"]
                        or page.locator(ASSISTANT).count() > record["assistant_before"])
        if conversation_url(page.url) and acknowledged:
            record.update(state="waiting", url=page.url)
            write_record(folder, record)
            return
        page.wait_for_timeout(200)
    raise BrowserProblem("submission", "Có thể prompt đã gửi nhưng chưa xác nhận được cuộc trò chuyện. Kiểm tra browser; app không tự gửi lại.")


def result_link(page, assistant_before=0):
    # Only files in assistant messages; never source attachments, sidebar or arbitrary links.
    messages = page.locator(ASSISTANT)
    if messages.count() <= assistant_before:
        return None
    # A prior answer's PPTX is not the result of the latest export request.
    for anchor in messages.last.locator('a[href]').all()[::-1]:
        label = (anchor.inner_text() + " " + (anchor.get_attribute("download") or "")).casefold()
        href = anchor.get_attribute("href") or ""
        if ".pptx" not in label and ".pptx" not in urlsplit(href).path.casefold():
            continue
        parsed = urlsplit(href)
        if (href.startswith(("sandbox:/mnt/data/", "/backend-api/files/", "blob:https://chatgpt.com/"))
                or parsed.scheme == "https" and (parsed.hostname == "chatgpt.com"
                or (parsed.hostname or "").endswith(".oaiusercontent.com"))):
            return anchor
    # The current web UI can render an artifact as a filename button rather
    # than an anchor. Only inspect the latest assistant answer, never user
    # attachments/sidebar files; the downloaded bytes are validated below.
    for button in messages.last.get_by_role("button", name=re.compile(r"^[^/\\\n]{1,240}\.pptx$", re.I)).all()[::-1]:
        if button.is_visible() and button.is_enabled():
            return button
    return None


def wait_result(page, folder, record, cancel, progress, timeout=900):
    deadline = time.monotonic() + timeout
    last_progress = 0
    last_text, stable_since = "", time.monotonic()
    while time.monotonic() < deadline:
        check_cancel(cancel)
        page_problem(page)
        generating = visible(page, STOP)
        before = record.get("assistant_before", 0)
        link = result_link(page, before)
        if link and not generating:
            return link
        messages = page.locator(ASSISTANT)
        if messages.count() > before and not generating:
            text = messages.last.inner_text()
            if text != last_text:
                last_text, stable_since = text, time.monotonic()
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


def receive_download(page, entry, cancel, timeout=45, progress=None):
    """Accept direct links or the file-preview → Download file UI."""
    check_cancel(cancel)
    downloads = []

    def received(download):
        downloads.append(download)
    page.on("download", received)
    try:
        filename = entry.get_attribute("aria-label") or entry.inner_text().strip()
        is_button = entry.evaluate("e => e.tagName === 'BUTTON' || e.getAttribute('role') === 'button'")
        if progress:
            progress("Đang mở thẻ PowerPoint từ câu trả lời ChatGPT…")
        try:
            entry.click(timeout=10000)
        except Exception as exc:
            raise BrowserProblem("download", "Chưa mở được thẻ PowerPoint của ChatGPT. Tool giữ kết quả để thử lại.") from exc
        deadline = time.monotonic() + timeout
        preview_clicked = False
        download_label = re.compile(r"^(Download file|Tải tệp xuống|Tải xuống)$", re.I)
        while time.monotonic() < deadline:
            check_cancel(cancel)
            if downloads:
                return downloads[0]
            page_problem(page)
            if is_button and not preview_clicked:
                matches = []
                for button in page.get_by_role("button", name=download_label).all():
                    if not button.is_visible() or not button.is_enabled():
                        continue
                    # Preview is portaled outside the assistant answer. Match
                    # its filename locally, never a page-wide Download button.
                    for panel in button.locator('xpath=ancestor::*').all()[::-1][:5]:
                        if (panel.evaluate("e => ['HTML','BODY','MAIN'].includes(e.tagName)")
                                or panel.get_by_role("button", name=download_label).count() != 1):
                            continue
                        if panel.get_by_text(filename, exact=True).count() or panel.get_by_role("button", name=filename, exact=True).count():
                            matches.append(button)
                            break
                if matches:
                    if progress:
                        progress("Đang bấm tải PowerPoint từ thẻ tệp ChatGPT…")
                    try:
                        # The web card overlays its open-file button across
                        # the download icon. Keyboard activation targets the
                        # enabled Download button, rather than that overlay.
                        matches[-1].press("Enter", timeout=10000)
                    except Exception as exc:
                        raise BrowserProblem("download", "Chưa bấm được nút tải trong thẻ PowerPoint. Tool giữ kết quả để thử lại.") from exc
                    preview_clicked = True
            page.wait_for_timeout(200)
        raise BrowserProblem("download", "Chưa tải được PowerPoint từ nút tệp của ChatGPT. Tool giữ cuộc trò chuyện để tự thử lại.")
    finally:
        page.remove_listener("download", received)


def convert(account, root, request_folder, cancel, progress, *, timeout=900, observed=None):
    with profile_lock(root, account["id"]):
        return _convert_locked(account, request_folder, cancel, progress, timeout=timeout, observed=observed)


def _convert_locked(account, request_folder, cancel, progress, *, timeout, observed):
    from playwright.sync_api import Error, sync_playwright

    from .browser_capabilities import detect_plan, select_best_model, select_reasoning

    request = load_request(request_folder)
    folder = Path(request["folder"])
    record = read_record(folder, account["id"])
    target = folder / "bai-giang-song-ngu.pptx"
    if record["state"] == "completed" and target.is_file():
        if target.stat().st_size > MAX_POWERPOINT_BYTES or record.get("sha256") != hashlib.sha256(target.read_bytes()).hexdigest():
            raise BrowserProblem("result", "PowerPoint đã tải bị thay đổi. Nhận lại kết quả từ cuộc trò chuyện trước khi dùng.")
        inspect_returned_deck(target)
        return {"path": str(target), "url": record["url"], "cached": True}
    files = [folder / name for name in request["attachments"]]
    if any(p.parent != folder or not p.is_file() or p.stat().st_size > document_limit(p) for p in files):
        raise BrowserProblem("attachments", "Tài liệu hoặc mẫu đã thiếu/thay đổi. Chuẩn bị gói mới trước khi gửi.")
    write_record(folder, record)
    stage = "starting"
    try:
        with sync_playwright() as playwright:
            progress("Đang mở phiên ChatGPT chạy ngầm…")
            context = open_context(playwright, account, background=True, cancel=cancel)
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(10000)
                stage = "session"
                navigate(page, record["url"] or CHATGPT, cancel)
                require_account(page, cancel)
                if record["state"] == "prepared" and conversation_url(page.url):
                    raise BrowserProblem("interface", "Web mở lại cuộc trò chuyện cũ. Tạo chat mới trước khi chuyển đổi bài mới.")
                stage = "model"
                plan = detect_plan(page, PROFILE)
                if record["state"] == "prepared":
                    model = select_best_model(page)
                    reasoning = select_reasoning(page)
                    record.update(plan=plan, model=model, reasoning=reasoning)
                    write_record(folder, record)
                    progress(f"Model đang dùng: {model} · quyền truy cập theo web ChatGPT.")
                if observed:
                    observed(account["id"], plan, record.get("model", ""))
                if record["state"] == "prepared":
                    stage = "upload"
                    progress("Đang đính kèm tài liệu và gửi prompt đã cấu hình…")
                    submit(page, folder, record, request["prompt"], cancel, files=files)
                elif not record["url"]:
                    raise BrowserProblem("submission", "Chưa rõ yêu cầu trước đã gửi hay chưa. Kiểm tra browser; app không gửi trùng.")
                elif record["state"] == "submitting":
                    # Resume a possibly sent follow-up by waiting, never by resending.
                    record["state"] = "waiting"
                    write_record(folder, record)
                stage = "waiting"
                link = wait_result(page, folder, record, cancel, progress, timeout)
                stage = "download"
                progress("Đang tải và kiểm tra PowerPoint kết quả…")
                download = receive_download(page, link, cancel, progress=progress)
                if Path(download.suggested_filename).suffix.casefold() != ".pptx":
                    raise BrowserProblem("download", "Tệp web trả về không phải PowerPoint .pptx.")
                downloaded = download.path()
                if not downloaded or Path(downloaded).stat().st_size > MAX_POWERPOINT_BYTES:
                    raise BrowserProblem("download", "PowerPoint tải về bị lỗi hoặc vượt 200 MB.")
                pending = folder / "ket-qua-chua-kiem-tra.pptx"
                download.save_as(str(pending))
                inspect_returned_deck(pending)
                pending.replace(target)
                record.update(state="completed", error="", stage="completed", sha256=hashlib.sha256(target.read_bytes()).hexdigest())
                write_record(folder, record)
                return {"path": str(target), "url": record["url"], "cached": False}
            finally:
                try:
                    context.close()
                except Error:
                    pass
    except Exception as exc:
        from playwright.sync_api import TimeoutError

        code = exc.code if isinstance(exc, BrowserProblem) else "download" if stage == "download" else (
            "upload" if stage == "upload" and isinstance(exc, TimeoutError) and record["state"] == "prepared" else "browser")
        record.update(error=code, stage=stage, failure_type=type(exc).__name__)
        # Keep the last durable send state and conversation URL for safe resume.
        write_record(folder, record)
        if isinstance(exc, (BrowserProblem, ValueError)):
            raise
        if stage == "upload" and isinstance(exc, TimeoutError) and record["state"] == "prepared":
            raise BrowserProblem("upload", "Chưa tải xong tài liệu lên ChatGPT. Chưa gửi bài; phiên đăng nhập vẫn được giữ.") from exc
        if code == "download":
            raise BrowserProblem(code, "Chưa tải được PowerPoint kết quả. Phiên đăng nhập và cuộc trò chuyện được giữ để tự thử lại.") from exc
        raise BrowserProblem(code, "Browser mất kết nối hoặc giao diện ChatGPT đã đổi. Yêu cầu được giữ lại để kiểm tra/tiếp tục.") from exc
