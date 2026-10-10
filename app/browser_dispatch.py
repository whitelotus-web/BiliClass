"""Use eligible accounts in order, switching only before any prompt was sent."""

import json
from pathlib import Path

from . import browser_automation as web
from .browser_health import quota_blocked, temporary_blocked


def unsent(record):
    return record["state"] == "prepared" and not record["url"] and record["followups"] == 0


def recoverable(record):
    return unsent(record) or record["state"] == "waiting" and web.conversation_url(record["url"])


def temporary_failure(code, record):
    # Upload/editor retries are safe only before submission. Once sent,
    # recovery stays on the saved conversation and never reuploads the source.
    return (recoverable(record) and code in {"network", "browser", "download"}
            or unsent(record) and code in {"upload", "interface"}
            or record["state"] == "waiting" and web.conversation_url(record["url"]) and code == "timeout")


def convert_available(accounts, root, folder, cancel, progress, *, observed=None, failed=None, converter=None,
                      retry_delays=(2, 5)):
    converter = converter or web.convert
    journal = Path(folder) / "browser-job.json"
    record = web.read_record(folder, json.loads(journal.read_text(encoding="utf-8"))["account_id"]) if journal.is_file() else None
    if record and not unsent(record):
        eligible = [a for a in accounts if a["id"] == record["account_id"]]
    else:
        eligible = [a for a in accounts if a.get("ready") and not quota_blocked(a) and not temporary_blocked(a)]
    if not eligible:
        raise web.BrowserProblem("login", "Không còn tài khoản dùng được. Kiểm tra trạng thái trong Browser AI.")
    if record and not unsent(record) and record["state"] != "completed":
        if not eligible[0].get("ready"):
            raise web.BrowserProblem("login", "Đăng nhập lại tài khoản của bài đã gửi để tiếp tục đúng cuộc trò chuyện.")
        if quota_blocked(eligible[0]):
            raise web.BrowserProblem("limit", "Tài khoản của bài đã gửi đang hết lượt. Chờ hạn mức được cấp lại để tiếp tục.")
    last_error = None
    for account in eligible:
        web.check_cancel(cancel)
        if record and unsent(record):
            record = web.read_record(folder, record["account_id"])
            if not unsent(record):
                raise web.BrowserProblem("submission", "Trạng thái gửi đã đổi. Giữ tài khoản của bài đang làm để kiểm tra.")
            record["account_id"] = account["id"]
            record["error"] = ""
            web.write_record(folder, record)
        for attempt in range(len(retry_delays) + 1):
            try:
                result = converter(account, root, folder, cancel, progress, observed=observed)
                return dict(result, account_id=account["id"])
            except web.BrowserProblem as exc:
                last_error = exc
                record = web.read_record(folder, account["id"])
                if (temporary_failure(exc.code, record)
                        and attempt < len(retry_delays) and not cancel.is_set()):
                    progress("Kết nối tạm gián đoạn; đang tự khôi phục và tiếp tục bài đã gửi…"
                             if record["url"] else "Đang tự khôi phục Chrome để tiếp tục tải tài liệu…")
                    if cancel.wait(retry_delays[attempt]):
                        web.check_cancel(cancel)
                    continue
                if failed:
                    failed(account["id"], exc.code, str(exc))
                if (exc.code not in {"limit", "login", "verification", "auth_response", "network", "browser"}
                        or not unsent(record) or cancel.is_set()):
                    raise
                progress("Tài khoản hiện tại chưa dùng được; đang thử tài khoản còn kết nối khác trước khi gửi bài…")
                break
    raise last_error
