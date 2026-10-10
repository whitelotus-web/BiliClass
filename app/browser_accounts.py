"""Machine-local browser profiles; never passwords or exported session tokens."""

import json
import os
import shutil
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID, uuid4

from .browser_health import (
    AUTH_ERRORS,
    RECOVERY_CHECK_INTERVAL,
    UNKNOWN_QUOTA_BACKOFF,
    health_due,
    quota_blocked,
    retry_delay,
    temporary_blocked,
)


class ProfileBusy(ValueError):
    code = "busy"


class BrowserAccounts:
    def __init__(self, directory):
        self.root = (Path(directory) / "browser_ai").resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "accounts.json"
        self.data = {"version": 1, "active": "", "automatic": True, "audio": True, "accounts": [],
                     "selection": "auto", "pending_login": ""}
        if self.path.exists():
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if loaded.get("version") != 1 or not isinstance(loaded.get("accounts"), list):
                raise ValueError("Danh sách Browser AI không hợp lệ.")
            self.data.update(loaded)
            migrated = False
            for account in self.data["accounts"]:
                self.profile(account["id"])
                if account.get("channel") not in {"msedge", "chrome"}:
                    raise ValueError("Browser của tài khoản không hợp lệ.")
                if account.get("profile_layout") != "chrome-v1":
                    # Never move/export Edge's cookies or mark a fresh Chrome
                    # folder ready just because the old browser was signed in.
                    account.update(channel="chrome", profile_layout="chrome-v1", ready=False,
                                   plan="unknown", model="", status="Cần đăng nhập trên Chrome")
                    for key in ("name", "email", "saved_at"):
                        account.pop(key, None)
                    account["last_error"] = {"code": "browser_changed",
                        "message": "Browser AI đã chuyển sang Chrome. Đăng nhập lại một lần để lưu phiên Chrome riêng."}
                    migrated = True
                if account.get("last_error", {}).get("code") in AUTH_ERRORS:
                    account.update(ready=False, status="Cần đăng nhập / xác minh")
            if self.data.get("selection") != "auto":
                self.data["selection"] = "auto"
                migrated = True
            if migrated:
                self.save()

    def save(self):
        temporary = self.root / (str(uuid4()) + ".tmp")
        try:
            temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)

    def profile(self, account_id):
        if str(UUID(account_id)) != account_id:
            raise ValueError("Mã tài khoản không hợp lệ.")
        target = self.root / "profiles" / account_id
        if (target.resolve().parent != (self.root / "profiles").resolve()
                or not target.resolve().is_relative_to(self.root) or target.is_symlink()):
            raise ValueError("Đường dẫn hồ sơ browser không hợp lệ.")
        return target

    def get(self, account_id=None):
        account_id = self.data["active"] if account_id is None else account_id
        for item in self.data["accounts"]:
            if item["id"] == account_id:
                parent = self.profile(account_id)
                target = parent / "chrome"
                if target.resolve().parent != parent.resolve() or target.is_symlink():
                    raise ValueError("Đường dẫn hồ sơ Chrome không hợp lệ.")
                return dict(item, channel="chrome", profile=str(target))
        raise ValueError("Đăng nhập ChatGPT trong Cài đặt → Browser AI.")

    def add(self, label, channel="chrome"):
        label = label.strip()
        if not label or len(label) > 100 or channel != "chrome":
            raise ValueError("Hồ sơ ChatGPT dùng Google Chrome; tên tối đa 100 ký tự.")
        item = {"id": str(uuid4()), "label": label, "channel": channel, "profile_layout": "chrome-v1",
                "status": "Chưa đăng nhập", "plan": "unknown", "ready": False}
        self.profile(item["id"]).mkdir(parents=True)
        self.data["accounts"].append(item)
        if not self.data["active"]:
            self.data["active"] = item["id"]
        self.save()
        return item

    def select(self, account_id):
        self.get(account_id)
        self.data["pending_login"] = ""
        self.data["active"] = account_id
        self.data["selection"] = "auto"
        self.save()

    def prefer_paid(self):
        self.data["selection"] = "auto"
        self.data["active"] = self.preferred()["id"]
        self.data["pending_login"] = ""
        self.save()

    def begin_login(self, account_id):
        self.get(account_id)
        # Keep the conversion preference intact while another account signs in.
        self.data["pending_login"] = account_id
        self.save()

    def update_status(self, account_id, status):
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                account["status"] = status
                self.save()
                return

    def login_error(self, account_id, code, message, *, retry_after_seconds=None):
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                if code in {"busy", "cancelled"}:
                    return
                account["last_error"] = {"code": code, "message": message}
                if code in AUTH_ERRORS:
                    account.update(ready=False, status="Cần đăng nhập / xác minh")
                if code in {"network", "browser"}:
                    account["connection_retry_at"] = time.time() + RECOVERY_CHECK_INTERVAL
                if code == "limit":
                    account["quota_limited"] = True
                    delay = retry_after_seconds if retry_after_seconds is not None else retry_delay(message)
                    retry_at = time.time() + (delay or UNKNOWN_QUOTA_BACKOFF)
                    # A session probe must not shorten an existing task cooldown.
                    if retry_at >= account.get("quota_retry_at", 0):
                        account.update(quota_retry_at=retry_at, quota_reset_known=bool(delay))
                account["checked_at"] = time.time()
                self.save()
                return

    def candidates(self):
        priority = {"plus": 3, "pro": 3, "business": 3, "enterprise": 3, "edu": 3, "go": 2, "free": 1}
        ready = [a for a in self.data["accounts"] if a.get("ready")
                 and not quota_blocked(a) and not temporary_blocked(a)]
        ready.sort(key=lambda a: (priority.get(a.get("plan"), 0), a["id"] == self.data["active"]), reverse=True)
        return [self.get(a["id"]) for a in ready]

    def preferred(self):
        candidates = self.candidates()
        if not candidates:
            if any(a.get("ready") and quota_blocked(a) for a in self.data["accounts"]):
                raise ValueError("Các tài khoản còn đăng nhập đã hết lượt dùng. Chờ hạn mức được cấp lại; không cần đăng nhập lại.")
            if any(a.get("ready") for a in self.data["accounts"]):
                raise ValueError("Kết nối browser tạm gián đoạn. Tool giữ phiên và sẽ kiểm tra lại; không cần đăng nhập lại.")
            raise ValueError("Đăng nhập ChatGPT trong Cài đặt → Browser AI.")
        return candidates[0]

    def observe(self, account_id, plan, model="", identity=None):
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                account.update(plan=plan, model=model, ready=True, checked_at=time.time(), status="Đã đăng nhập · Tự lưu")
                account.pop("connection_retry_at", None)
                if account.get("last_error", {}).get("code") != "limit":
                    account.pop("last_error", None)
                if identity is not None:
                    account.update(name=identity.get("name", ""), email=identity.get("email", ""), saved_at=time.time())
                    account["label"] = account["email"] or account["name"] or account["label"]
                    if self.data.get("pending_login") == account_id:
                        self.data["pending_login"] = ""
                if self.data.get("selection") != "manual":
                    if self.candidates():
                        self.data["active"] = self.preferred()["id"]
                self.save()
                return

    def conversion_succeeded(self, account_id):
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                account["quota_limited"] = False
                for key in ("quota_retry_at", "quota_reset_known", "connection_retry_at"):
                    account.pop(key, None)
                if account.get("last_error", {}).get("code") in {"limit", "network", "browser"}:
                    account.pop("last_error", None)
                account["completed_at"] = time.time()
                self.save()
                return

    def due_accounts(self):
        return sorted((a["id"] for a in self.data["accounts"] if health_due(a)),
                      key=lambda account_id: max(self.get(account_id).get("checked_at", 0),
                                                 self.get(account_id).get("probe_attempted_at", 0)))

    def probe_started(self, account_id):
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                account["probe_attempted_at"] = time.time()
                self.save()
                return

    def remove(self, account_id):
        item = self.get(account_id)
        # A real OS lock prevents removal while login or conversion uses the profile.
        with profile_lock(self.root, account_id):
            from .chrome_session import require_idle_profile

            require_idle_profile(Path(item["profile"]))
            target = self.profile(account_id)
            if target.exists():
                shutil.rmtree(target)
            self.data["accounts"] = [a for a in self.data["accounts"] if a["id"] != item["id"]]
            if self.data.get("pending_login") == account_id:
                self.data["pending_login"] = ""
            if self.data["active"] == account_id:
                self.data["active"] = self.data["accounts"][0]["id"] if self.data["accounts"] else ""
                self.data["selection"] = "auto"
                if self.candidates():
                    self.data["active"] = self.preferred()["id"]
            self.save()

    def options(self, automatic, audio):
        self.data.update(automatic=bool(automatic), audio=bool(audio))
        self.save()


@contextmanager
def profile_lock(root, account_id):
    if str(UUID(account_id)) != account_id:
        raise ValueError("Mã tài khoản không hợp lệ.")
    directory = Path(root) / "locks"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / (account_id + ".lock")).open("a+b") as handle:
        handle.seek(0, 2)
        if not handle.tell():
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ProfileBusy("Tài khoản đang được sử dụng. Đóng phiên đăng nhập hoặc chờ chuyển đổi xong.") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
