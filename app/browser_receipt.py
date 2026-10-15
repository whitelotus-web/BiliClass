"""Recover a send acknowledgement using visible messages, never resubmission.

The intent is local to the request. Only this account's recent conversation
links are inspected, with a bounded scan and a complete prompt comparison.
No cookie, token, private endpoint or chat history is exported.
"""

import hashlib
import re
import time
from pathlib import Path


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def save_intent(folder, record, prompt):
    path = Path(folder) / "send-intent.txt"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(prompt, encoding="utf-8")
    temporary.replace(path)
    record["send_sha256"] = hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def intent_prompt(folder, record, request):
    from .browser_automation import EXPORT_PROMPT, BrowserProblem

    if record.get("send_sha256"):
        try:
            prompt = (Path(folder) / "send-intent.txt").read_text(encoding="utf-8")
        except OSError as exc:
            raise BrowserProblem("record", "Thiếu bản ghi prompt đã gửi; giữ bài để kiểm tra, không gửi lại.") from exc
        if hashlib.sha256(prompt.encode("utf-8")).hexdigest() != record["send_sha256"]:
            raise BrowserProblem("record", "Bản ghi prompt đã thay đổi; giữ bài để kiểm tra, không gửi lại.")
        return prompt
    # Read older jobs without modifying their durable send state.
    if record.get("quality_stage") in {"submitting", "waiting"}:
        raise BrowserProblem("submission", "Yêu cầu sửa cũ chưa có xác nhận gửi. Mở đúng cuộc trò chuyện để kiểm tra.")
    return EXPORT_PROMPT if record.get("followups") else request["prompt"]


def matching_users(page, prompt):
    from .browser_automation import USER

    wanted = normalized(prompt)
    # The web may put filenames/role labels around the prompt. Require the
    # complete text, not a title, filename or an assistant's quoted reply.
    nodes = page.locator(USER).all()
    if nodes and wanted not in normalized(nodes[-1].inner_text()):
        # Expanding older turns scrolls a virtualized chat away from the new
        # response and invalidates DOM indices. Only the latest user turn can
        # acknowledge this tool's pending send. Still detect visible duplicates.
        for button in nodes[-1].get_by_role("button", name=re.compile(
                r"^(Show more|Xem thêm|Hiển thị thêm)$", re.I)).all():
            if button.is_visible():
                button.click(timeout=5000)
    return [index for index,node in enumerate(page.locator(USER).all())
            if wanted and wanted in normalized(node.inner_text())]


def wait_receipt(page, folder, record, prompt, cancel, *, previous_url="", timeout=40):
    from . import browser_automation as web

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        web.check_cancel(cancel)
        web.page_problem(page)
        # The current web virtualizes old turns: adding a user turn can leave
        # the total count unchanged or lower, even at the same chat URL.
        # The exact latest prompt is another positive acknowledgement.
        indices = matching_users(page, prompt)
        acknowledged = (indices == [page.locator(web.USER).count()-1]
                        or page.url != previous_url
                        or page.locator(web.USER).count() > record['user_before']
                        or page.locator(web.ASSISTANT).count() > record['assistant_before'])
        if web.conversation_url(page.url) and acknowledged:
            record.update(state="waiting", url=page.url, error="")
            web.write_record(folder, record)
            return True
        page.wait_for_timeout(200)
    return False


def recover_submission(context, page, folder, record, request, cancel, *, limit=10):
    from . import browser_automation as web

    prompt = intent_prompt(folder, record, request)
    # Prefer a saved conversation; otherwise inspect restored tabs and a small
    # recent-history list. Never navigate an arbitrary external link.
    candidates = []
    if record["url"]:
        candidates.append(record["url"])
    else:
        candidates.extend(p.url for p in context.pages if web.conversation_url(p.url))
    web.navigate(page, record["url"] or web.CHATGPT, cancel)
    web.require_account(page, cancel)
    if not record["url"]:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            web.check_cancel(cancel)
            links = page.locator('nav a[href^="/c/"], aside a[href^="/c/"], [data-testid="history"] a[href^="/c/"]').all()
            candidates.extend(web.CHATGPT.rstrip("/") + node.get_attribute("href") for node in links)
            if links:
                break
            page.wait_for_timeout(250)
    candidates = list(dict.fromkeys(url for url in candidates if web.conversation_url(url)))[:limit]
    matches = []
    for url in candidates:
        web.check_cancel(cancel)
        web.navigate(page, url, cancel)
        web.require_account(page, cancel)
        # Composer can appear before messages during hydration.
        deadline = time.monotonic() + 5
        while not page.locator(web.USER).count() and time.monotonic() < deadline:
            web.check_cancel(cancel)
            web.page_problem(page)
            page.wait_for_timeout(250)
        indices = matching_users(page, prompt)
        if len(indices) > 1:
            raise web.BrowserProblem("submission", "Có nhiều yêu cầu trùng nội dung; cần kiểm tra đúng cuộc trò chuyện. Tool không gửi lại.")
        if indices == [page.locator(web.USER).count()-1]:
            matches.append(url)
    if not matches:
        raise web.BrowserProblem("receipt", "Chưa tìm được xác nhận gửi trong các cuộc trò chuyện gần đây. Đã giữ yêu cầu để kiểm tra; không gửi lại khi kết quả gửi chưa rõ.")
    if len(matches) != 1:
        raise web.BrowserProblem("submission", "Chưa xác định được duy nhất cuộc trò chuyện đã gửi. Yêu cầu được giữ; cần mở browser kiểm tra, không gửi lại bài.")
    web.navigate(page, matches[0], cancel)
    web.require_account(page, cancel)
    record.update(state="waiting", url=matches[0], error="")
    web.write_record(folder, record)
    return page
