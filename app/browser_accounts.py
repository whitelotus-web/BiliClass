"""Machine-local browser profiles; never passwords or exported session tokens."""

import json
import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID, uuid4


class ProfileBusy(ValueError):
    pass


class BrowserAccounts:
    def __init__(self, directory):
        self.root = (Path(directory) / "browser_ai").resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "accounts.json"
        self.data = {"version": 1, "active": "", "automatic": True, "audio": True, "accounts": []}
        if self.path.exists():
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if loaded.get("version") != 1 or not isinstance(loaded.get("accounts"), list):
                raise ValueError("Danh sách Browser AI không hợp lệ.")
            self.data.update(loaded)
            for account in self.data["accounts"]:
                self.profile(account["id"])
                if account.get("channel") not in {"msedge", "chrome"}:
                    raise ValueError("Browser của tài khoản không hợp lệ.")

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
                return dict(item, profile=str(self.profile(account_id)))
        raise ValueError("Thêm và chọn tài khoản trong Cài đặt → Browser AI.")

    def add(self, label, channel):
        label = label.strip()
        if not label or len(label) > 100 or channel not in {"msedge", "chrome"}:
            raise ValueError("Nhập tên tài khoản (tối đa 100 ký tự) và chọn Edge hoặc Chrome.")
        item = {"id": str(uuid4()), "label": label, "channel": channel, "status": "Chưa kiểm tra đăng nhập"}
        self.profile(item["id"]).mkdir(parents=True)
        self.data["accounts"].append(item)
        if not self.data["active"]:
            self.data["active"] = item["id"]
        self.save()
        return item

    def select(self, account_id):
        self.get(account_id)
        self.data["active"] = account_id
        self.save()

    def update_status(self, account_id, status):
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                account["status"] = status
                self.save()
                return

    def remove(self, account_id):
        item = self.get(account_id)
        # A real OS lock prevents removal while login or conversion uses the profile.
        with profile_lock(self.root, account_id):
            target = self.profile(account_id)
            if target.exists():
                shutil.rmtree(target)
            self.data["accounts"] = [a for a in self.data["accounts"] if a["id"] != item["id"]]
            if self.data["active"] == account_id:
                self.data["active"] = self.data["accounts"][0]["id"] if self.data["accounts"] else ""
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
