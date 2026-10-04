"""Use eligible accounts in order, switching only before any prompt was sent."""

import json
from pathlib import Path

from . import browser_automation as web


def unsent(record):
    return record["state"] == "prepared" and not record["url"] and record["followups"] == 0


def convert_available(accounts, root, folder, cancel, progress, *, observed=None, failed=None, converter=None):
    converter = converter or web.convert
    journal = Path(folder) / "browser-job.json"
    record = web.read_record(folder, json.loads(journal.read_text(encoding="utf-8"))["account_id"]) if journal.is_file() else None
    if record and not unsent(record):
        eligible = [a for a in accounts if a["id"] == record["account_id"]]
    else:
        eligible = [a for a in accounts if a.get("ready") and not a.get("quota_limited")]
    if not eligible:
        raise web.BrowserProblem("login", "Không còn tài khoản dùng được. Kiểm tra trạng thái trong Browser AI.")
    if record and not unsent(record):
        if not eligible[0].get("ready"):
            raise web.BrowserProblem("login", "Đăng nhập lại tài khoản của bài đã gửi để tiếp tục đúng cuộc trò chuyện.")
        if eligible[0].get("quota_limited"):
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
        try:
            result = converter(account, root, folder, cancel, progress, observed=observed)
            return dict(result, account_id=account["id"])
        except web.BrowserProblem as exc:
            last_error = exc
            if failed:
                failed(account["id"], exc.code, str(exc))
            record = web.read_record(folder, account["id"])
            if (exc.code not in {"limit", "login", "verification", "auth_response", "network", "browser"}
                    or not unsent(record) or cancel.is_set()):
                raise
            progress("Tài khoản hiện tại chưa dùng được; đang thử tài khoản còn kết nối khác trước khi gửi bài…")
    raise last_error
