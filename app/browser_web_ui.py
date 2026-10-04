"""Qt controls for isolated ChatGPT web sessions, including Free accounts."""

import json
from datetime import datetime
from pathlib import Path
from threading import Event

from PySide6.QtCore import Property, QObject, QThread, QTimer, Signal, Slot

from . import browser_automation
from .browser_accounts import BrowserAccounts


class WebLoginJob(QThread):
    progress = Signal(str)

    def __init__(self, account, root, parent, *, url="", resume=False):
        super().__init__(parent)
        self.account, self.root = account, root
        self.url, self.resume = url, resume
        self.request_folder = parent.bridge.chatgptRequest.get("folder", "") if resume else ""
        self.cancel = Event()
        self.result, self.error, self.error_code = None, "", ""

    def run(self):
        try:
            options = {"url": self.url} if self.url else {}
            self.result = browser_automation.login(self.account, self.root, self.cancel, self.progress.emit, **options)
        except (browser_automation.BrowserProblem, ValueError) as exc:
            self.error = str(exc)
            self.error_code = getattr(exc, "code", "browser")
        except Exception:
            self.error = "Chưa mở được phiên ChatGPT. Kiểm tra mạng và thử lại."
            self.error_code = "browser"


class WebBrowserAI(QObject):
    changed = Signal()
    progress = Signal(str)
    observed = Signal(str, str, str)
    failed = Signal(str, str, str)

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.store = BrowserAccounts(bridge.library.directory)
        self.job = None
        self._error = False
        self._error_code = ""
        self._message = "Đăng nhập ChatGPT Free hoặc Plus trong cửa sổ riêng. Phiên được tự lưu trên máy."
        self._restore_error()
        self.observed.connect(self._observed)
        self.failed.connect(self._failed)

    def _restore_error(self):
        try:
            error = self.store.get(self.activeId).get("last_error", {})
        except ValueError:
            error = {}
        self._error_code = error.get("code", "")
        self._error = bool(error)
        if error:
            self._message = error["message"]

    @Property(bool, notify=changed)
    def verificationBlocked(self):
        return self._error_code == "verification"

    @Property(bool, constant=True)
    def webMode(self):
        return True

    @Property("QVariantList", notify=changed)
    def accounts(self):
        return self.store.data["accounts"]

    @Property(str, notify=changed)
    def activeId(self):
        # A failed newly added account remains visible and retryable, without
        # changing which verified account new conversion jobs prefer.
        return self.store.data.get("pending_login") or self.store.data["active"]

    @Property(str, notify=changed)
    def activeLabel(self):
        try:
            return self.store.preferred()["label"]
        except ValueError:
            return "Chưa đăng nhập"

    @Property(bool, notify=changed)
    def autoSelection(self):
        return self.store.data.get("selection") != "manual"

    @Property(str, notify=changed)
    def selectionLabel(self):
        return "Tự động · ưu tiên Plus" if self.autoSelection else "Cố định · " + self.activeLabel

    @Property("QVariantMap", notify=changed)
    def accountInfo(self):
        try:
            account = self.store.get(self.activeId)
        except ValueError:
            return {}
        saved = account.get("saved_at")
        return {"label": account["label"], "name": account.get("name", ""), "email": account.get("email", ""),
                "ready": account.get("ready", False), "plan": account.get("plan", "unknown"),
                "saved": datetime.fromtimestamp(saved).strftime("%H:%M · %d/%m/%Y") if saved else "Chưa xác nhận",
                "model": account.get("model", "")}

    @Property(str, notify=changed)
    def quotaMessage(self):
        return "Web chưa cung cấp số dư hạn mức cho tool. Nếu gặp giới hạn, bài sẽ dừng và giữ kết quả đã nhận."

    @Property(bool, notify=changed)
    def hasError(self):
        return self._error and not self.job

    @Property(bool, notify=changed)
    def automatic(self):
        return self.store.data["automatic"]

    @Property(bool, notify=changed)
    def audio(self):
        return self.store.data["audio"]

    @Property(bool, notify=changed)
    def loginBusy(self):
        return self.job is not None

    @Property(bool, constant=True)
    def disconnectBusy(self):
        return False

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Slot(str)
    def inform(self, message):
        self._message = message
        self.changed.emit()

    def _available(self):
        if self.job or self.bridge.busy:
            self.inform("Chờ tác vụ hiện tại xong trước khi quản lý tài khoản.")
            return False
        return True

    @Slot(str)
    def select(self, account_id):
        if self._available():
            self.store.select(account_id)
            self._restore_error()
            self.inform(self._message if self.hasError else "Bài mới sẽ dùng tài khoản đã chọn, kể cả khi có Plus.")

    @Slot()
    def preferPaid(self):
        if self._available():
            try:
                self.store.prefer_paid()
                self._restore_error()
                self.inform("Bài mới ưu tiên Plus trước Free. Bài đã gửi giữ nguyên tài khoản.")
            except ValueError as exc:
                self.inform(str(exc))

    @Slot(str)
    def remove(self, account_id):
        if self._available():
            try:
                self.store.remove(account_id)
                self._restore_error()
                self.inform("Đã xóa tài khoản và phiên web riêng trên máy.")
            except (ValueError, OSError):
                self.inform("Chưa xóa được phiên. Đóng cửa sổ đăng nhập rồi thử lại.")

    @Slot(bool, bool)
    def saveOptions(self, automatic, audio):
        self.store.options(automatic, audio)
        self.changed.emit()

    @Slot()
    def connectAccount(self):
        if self.job:
            self.job.cancel.set()
            self.inform("Đang đóng cửa sổ đăng nhập…")
        elif self.accountInfo.get("ready") and not self.store.data.get("pending_login"):
            self.addAndSignIn()
        else:
            self.signIn(self.activeId)

    @Slot()
    def useManualBrowser(self):
        if not self._available():
            return
        # Explicit user choice only; normal-browser sign-in is not a saved
        # connection and must never flip ready or unlock background jobs.
        self.store.options(False, self.audio)
        self.inform("Đã chọn gửi/nhận thủ công. Nhập bài để tạo prompt và gói tài liệu; tài khoản tự động chưa kết nối.")
        self.bridge.navigate.emit("new")

    @Slot()
    def addAndSignIn(self):
        self.signIn("")

    @Slot(str)
    def signIn(self, account_id, *, url="", resume=False):
        if not self._available():
            return
        if not account_id:
            account_id = self.store.add(f"ChatGPT {len(self.accounts) + 1}")["id"]
        self.store.begin_login(account_id)
        self._error = False
        self._error_code = ""
        self.job = WebLoginJob(self.store.get(account_id), self.store.root, self, url=url, resume=resume)
        self.job.progress.connect(self.inform)
        self.job.finished.connect(self._finished)
        self.job.start()
        self.inform("Đang mở ChatGPT trong Edge riêng. Đăng nhập trực tiếp ở cửa sổ vừa mở…")

    @Slot()
    def _finished(self):
        job, self.job = self.job, None
        if job.error:
            self._error = True
            self._error_code = job.error_code
            self.store.login_error(job.account["id"], job.error_code, job.error)
            self.inform(job.error)
        elif job.result and job.result.get("ready"):
            self.store.observe(job.account["id"], job.result.get("plan", "unknown"), identity=job.result)
            self._error = False
            self._error_code = ""
            self.inform("Đã đăng nhập và lưu phiên web. Có thể chuyển đổi bài giảng.")
        else:
            self.inform("Chưa xác nhận đăng nhập mới. Bấm Đăng nhập để tiếp tục.")
        if job.resume and job.result and job.result.get("ready") and not job.cancel.is_set():
            # User requested recovery of this job; continue only after the
            # visible login confirms the same saved browser profile.
            QTimer.singleShot(0, lambda folder=job.request_folder: self._continue_request(folder))
        job.deleteLater()

    def _continue_request(self, folder):
        if folder and self.bridge.chatgptRequest.get("folder") == folder:
            self.bridge.runBrowserAI()
        else:
            self.inform("Đã đăng nhập. Bài đang mở đã đổi; mở lại gói cũ để tiếp tục chuyển đổi.")

    @Slot(str, str, str)
    def _observed(self, account_id, plan, model):
        self.store.observe(account_id, plan, model)
        self._restore_error()
        self.changed.emit()

    @Slot(str, str, str)
    def _failed(self, account_id, code, message):
        self.store.login_error(account_id, code, message)
        if code in {"login", "verification"}:
            self.store.begin_login(account_id)
        self._restore_error()
        self.inform(message)

    def conversionAccount(self, folder=""):
        journal = Path(folder) / "browser-job.json" if folder else None
        if journal and journal.is_file():
            record = json.loads(journal.read_text(encoding="utf-8"))
            return self.store.get(record["account_id"])
        return self.store.preferred()

    @Slot()
    def openUsage(self):
        self.signIn(self.activeId)

    def shutdown(self):
        if self.job:
            self.job.cancel.set()
            self.job.wait()
