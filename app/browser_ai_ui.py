"""Minimal Qt account controls for official ChatGPT plan authorization."""

import json
from pathlib import Path
from threading import Event

from PySide6.QtCore import Property, QObject, QThread, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from .chatgpt_auth import USAGE_URL, ChatGPTAuth, PlanAccounts, PlanError


class LoginJob(QThread):
    progress = Signal(str)

    def __init__(self, store, account_id, parent, disconnect=False):
        super().__init__(parent)
        self.store, self.account_id, self.disconnect = store, account_id, disconnect
        self.cancel = Event()
        self.result, self.error = None, ""

    def run(self):
        auth = ChatGPTAuth(self.store)
        try:
            if self.disconnect:
                self.result = {"removed": True, "confirmed": auth.disconnect(self.account_id)}
            else:
                self.result = auth.authorize(self.account_id, self.cancel, self.progress.emit)
        except PlanError as exc:
            self.error = str(exc)
        except Exception:
            self.error = "Chưa kết nối được ChatGPT. Kiểm tra mạng và thử đăng nhập lại."
        finally:
            auth.client.close()


class BrowserAI(QObject):
    changed = Signal()
    progress = Signal(str)

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.store = PlanAccounts(bridge.library.directory)
        self.job = None
        self._message = "Đăng nhập một lần, cho phép dùng hạn mức ChatGPT; kết nối tự lưu trên máy."
        legacy = Path(bridge.library.directory) / "browser_ai/accounts.json"
        if legacy.is_file() and not self.store.path.exists():
            try:
                old = json.loads(legacy.read_text(encoding="utf-8"))
                self.store.options(old.get("automatic", True), old.get("audio", True))
                if old.get("accounts"):
                    self._message = "Kết nối chính thức cần đăng nhập lại một lần. Hồ sơ web cũ vẫn được giữ tại máy."
            except (ValueError, OSError):
                pass

    @Property("QVariantList", notify=changed)
    def accounts(self):
        return self.store.data["accounts"]

    @Property(str, notify=changed)
    def activeId(self):
        return self.store.data["active"]

    @Property(str, notify=changed)
    def activeLabel(self):
        try:
            return self.store.get()["label"]
        except ValueError:
            return "Chưa kết nối"

    @Property(bool, notify=changed)
    def automatic(self):
        return self.store.data["automatic"]

    @Property(bool, notify=changed)
    def audio(self):
        return self.store.data["audio"]

    @Property(bool, notify=changed)
    def loginBusy(self):
        return self.job is not None

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Slot(str)
    def inform(self, message):
        self._message = message
        self.changed.emit()

    @Slot(str)
    def select(self, account_id):
        if self.bridge.busy or self.job:
            self.inform("Chờ tác vụ hiện tại xong trước khi đổi tài khoản.")
            return
        try:
            self.store.select(account_id)
            self.changed.emit()
        except ValueError as exc:
            self.inform(str(exc))

    @Slot(str)
    def remove(self, account_id):
        self._open(account_id, disconnect=True)

    @Slot(bool, bool)
    def saveOptions(self, automatic, audio):
        self.store.options(automatic, audio)
        self.inform("Đã lưu cách chuyển đổi và chuẩn bị giọng đọc.")

    @Slot(str)
    def signIn(self, account_id):
        self._open(account_id)

    @Slot()
    def addAndSignIn(self):
        self._open("")

    def conversionAccount(self, folder=""):
        journal = Path(folder) / "ai-job.json" if folder else None
        if journal and journal.is_file():
            record = json.loads(journal.read_text(encoding="utf-8"))
            return self.store.get(record["account_id"])
        if folder and (Path(folder) / "browser-job.json").is_file():
            raise PlanError("Đây là yêu cầu web cũ. Nhận PowerPoint thủ công hoặc tạo yêu cầu mới bằng kết nối chính thức.")
        return self.store.get()

    @Slot()
    def openConversation(self):
        self.bridge.openChatGPT()

    @Slot()
    def openUsage(self):
        if not QDesktopServices.openUrl(QUrl(USAGE_URL)):
            self.inform("Chưa mở được trang hạn mức ChatGPT trong trình duyệt mặc định.")

    def _open(self, account_id, disconnect=False):
        if self.job or self.bridge.busy:
            self.inform("Chờ tác vụ hiện tại xong trước khi quản lý kết nối.")
            return
        self.job = LoginJob(self.store, account_id, self, disconnect)
        self.job.progress.connect(self.inform)
        self.job.finished.connect(self._finished)
        self.job.start()
        self.inform("Đang ngắt kết nối…" if disconnect else "Đang mở cửa sổ Edge riêng của BiliClass để đăng nhập ChatGPT…")

    @Slot()
    def stopLogin(self):
        if self.job and not self.job.disconnect:
            self.job.cancel.set()
            self.inform("Đang hủy đăng nhập và đóng cửa sổ riêng của BiliClass…")

    @Slot()
    def _finished(self):
        job, self.job = self.job, None
        self.store.reload()
        if job.error:
            self.inform(job.error)
        elif job.disconnect:
            self.inform("Đã ngắt kết nối." if job.result["confirmed"] else
                        "Đã xóa phiên tại máy; chưa xác nhận thu hồi trên mạng. Có thể quản lý quyền trong ChatGPT.")
        elif job.result["ready"]:
            self.inform("Đã kết nối và tự lưu. Chuyển đổi bài sử dụng hạn mức gói ChatGPT của tài khoản này.")
        else:
            self.inform("Đã đăng nhập, chưa được cấp quyền xử lý bằng hạn mức ChatGPT. Có thể dùng gửi/nhận thủ công.")
        job.deleteLater()

    def shutdown(self):
        if self.job:
            self.job.cancel.set()
            self.job.wait()
