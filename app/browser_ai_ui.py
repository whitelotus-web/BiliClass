"""Qt controls for account profiles and an interruptible manual login window."""

import json
from pathlib import Path
from threading import Event

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from .browser_accounts import BrowserAccounts
from .browser_automation import CHATGPT, login


class LoginJob(QThread):
    completed = Signal(object, str)
    progress = Signal(str)

    def __init__(self, account, root, parent, url, auto_close):
        super().__init__(parent)
        self.account, self.root, self.url = account, root, url
        self.cancel = Event()
        self.auto_close = auto_close
        self.result, self.error = None, ""

    def run(self):
        try:
            self.result = login(self.account, self.root, self.cancel, self.progress.emit, self.url, auto_close=self.auto_close)
        except Exception as exc:
            self.error = str(exc)
        self.completed.emit(self.result, self.error)


class BrowserAI(QObject):
    changed = Signal()
    progress = Signal(str)
    observed = Signal(str, str, str)

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.store = BrowserAccounts(bridge.library.directory)
        self.job = None
        self._message = "Đăng nhập trên web; phiên được tự lưu trên máy này."
        self.observed.connect(self._observed)

    @Property("QVariantList", notify=changed)
    def accounts(self):
        return self.store.data["accounts"]

    @Property(str, notify=changed)
    def activeId(self):
        return self.store.data["active"]

    @Property(str, notify=changed)
    def activeLabel(self):
        try:
            return self.store.preferred()["label"]
        except ValueError:
            return "Chưa đăng nhập"

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

    @Slot(str, str)
    def add(self, label, channel):
        try:
            item = self.store.add(label, channel)
            self.inform("Đã thêm hồ sơ. Bấm Đăng nhập để truy cập tài khoản ChatGPT trên web.")
            self.select(item["id"])
        except Exception as exc:
            self.inform(str(exc))

    @Slot(str)
    def select(self, account_id):
        if self.bridge.busy:
            self.inform("Chờ chuyển đổi xong trước khi đổi tài khoản.")
            return
        try:
            self.store.select(account_id)
            self.changed.emit()
        except Exception as exc:
            self.inform(str(exc))

    @Slot(str)
    def remove(self, account_id):
        if self.bridge.busy or self.job:
            self.inform("Đóng phiên đăng nhập và chờ tác vụ xong trước khi xóa hồ sơ.")
            return
        try:
            self.store.remove(account_id)
            self.inform("Đã xóa hồ sơ và phiên đăng nhập trên máy. Tài khoản ChatGPT trên web vẫn tồn tại.")
        except Exception as exc:
            self.inform(str(exc))

    @Slot(bool, bool)
    def saveOptions(self, automatic, audio):
        self.store.options(automatic, audio)
        self.inform("Đã lưu cách chuyển đổi và chuẩn bị giọng đọc.")

    @Slot(str)
    def signIn(self, account_id):
        self._open(account_id, CHATGPT)

    @Slot()
    def addAndSignIn(self):
        if self.job or self.bridge.busy:
            self.inform("Chờ tác vụ hiện tại xong trước khi đăng nhập.")
            return
        try:
            used = {item["label"] for item in self.accounts}
            number = 1
            while f"ChatGPT {number}" in used:
                number += 1
            account = self.store.add(f"ChatGPT {number}")
            self.changed.emit()
            self._open(account["id"], CHATGPT)
        except Exception as exc:
            self.inform(str(exc))

    def conversionAccount(self, folder=""):
        journal = Path(folder) / "browser-job.json" if folder else None
        if journal and journal.is_file():
            record = json.loads(journal.read_text(encoding="utf-8"))
            return self.store.get(record["account_id"])
        return self.store.preferred()

    @Slot()
    def openConversation(self):
        from .browser_automation import read_record

        try:
            request = self.bridge.chatgptRequest
            if request:
                account = self.conversionAccount(request["folder"])
                record = read_record(request["folder"], account["id"])
                self._open(account["id"], record.get("url") or CHATGPT, auto_close=False)
        except Exception as exc:
            self.inform(str(exc))

    def _open(self, account_id, url, *, auto_close=True):
        if self.job or self.bridge.busy:
            self.inform("Chờ tác vụ xong hoặc dừng tác vụ rồi mở browser.")
            return
        try:
            account = self.store.get(account_id)
            self.job = LoginJob(account, self.store.root, self, url, auto_close)
            self.job.progress.connect(self.inform)
            self.job.finished.connect(self._finished)
            self.job.start()
            self.inform("Đang mở browser đăng nhập…")
        except Exception as exc:
            self.inform(str(exc))

    @Slot()
    def stopLogin(self):
        if self.job:
            self.job.cancel.set()

    @Slot()
    def _finished(self):
        job, self.job = self.job, None
        message = job.error or job.result["message"]
        if job.result and job.result["ready"]:
            self.store.observe(job.account["id"], job.result.get("plan", "unknown"))
        elif job.auto_close:
            self.store.update_status(job.account["id"], message)
        self.inform(message)
        job.deleteLater()

    @Slot(str, str, str)
    def _observed(self, account_id, plan, model):
        self.store.observe(account_id, plan, model)
        self.changed.emit()

    def shutdown(self):
        if self.job:
            self.job.cancel.set()
            self.job.wait()
