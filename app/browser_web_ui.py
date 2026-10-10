"""Qt controls for isolated ChatGPT web sessions, including Free accounts."""

import json
from datetime import datetime
from pathlib import Path
from threading import Event

from PySide6.QtCore import Property, QObject, QThread, QTimer, Signal, Slot

from . import browser_automation
from .browser_accounts import BrowserAccounts
from .browser_health import quota_blocked


class WebLoginJob(QThread):
    progress = Signal(str)
    confirmation = Signal(bool)

    def __init__(self, account, root, parent, *, url="", resume=False, check_only=False):
        super().__init__(parent)
        self.account, self.root = account, root
        self.url, self.resume = url, resume
        self.check_only = check_only
        self.request_folder = parent.bridge.chatgptRequest.get("folder", "") if resume else ""
        self.cancel = Event()
        self.finish_login = Event()
        self.result, self.error, self.error_code = None, "", ""

    def run(self):
        try:
            if self.check_only:
                self.result = browser_automation.check_session(self.account, self.root, self.cancel, self.progress.emit)
                return
            options = {"url": self.url} if self.url else {}
            self.result = browser_automation.login(self.account, self.root, self.cancel, self.progress.emit,
                finish=self.finish_login, awaiting_confirmation=self.confirmation.emit, **options)
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
    succeeded = Signal(str)

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.store = BrowserAccounts(bridge.library.directory)
        self.job = None
        self._after_probe = ""
        self._awaiting_confirmation = False
        self._error = False
        self._error_code = ""
        self._message = "Đăng nhập ChatGPT Free hoặc Plus trong cửa sổ riêng. Phiên được tự lưu trên máy."
        self._restore_error()
        self._health_timer = QTimer(self)
        self._health_timer.setInterval(60000)
        self._health_timer.timeout.connect(self.refreshAccounts)
        self._health_timer.start()
        self.observed.connect(self._observed)
        self.failed.connect(self._failed)
        self.succeeded.connect(self._succeeded)

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
        rows = []
        for account in self.store.data["accounts"]:
            checking = self.job is not None and self.job.account["id"] == account["id"]
            code = account.get("last_error", {}).get("code", "")
            connected = account.get("ready", False)
            limited = account.get("quota_limited", False)
            if checking:
                status, color = ("Đang kiểm tra…" if self.job.check_only else "Đang đăng nhập…"), "#0869f9"
            elif connected:
                if limited:
                    status, color = ("Đã đăng nhập · Hết lượt dùng" if quota_blocked(account)
                                     else "Đã đăng nhập · Có thể thử lại"), "#ab5b20"
                elif code in {"network", "browser"}:
                    status, color = "Kết nối tạm gián đoạn", "#ab5b20"
                else:
                    status, color = "Đã đăng nhập", "#138578"
            else:
                status, color = ("Mất kết nối", "#c05b31") if account.get("saved_at") else ("Chưa đăng nhập", "#667997")
            rows.append({"id": account["id"], "label": account["label"], "name": account.get("name", ""),
                         "email": account.get("email", ""), "plan": account.get("plan", "unknown"),
                         "ready": connected, "limited": limited, "status": status, "color": color,
                         "checking": checking, "recheck": limited or code in {"network", "browser"},
                         "error": account.get("last_error", {}).get("message", "")})
        return rows

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

    @Property(bool, notify=changed)
    def loginAwaitingConfirmation(self):
        return self.job is not None and self._awaiting_confirmation

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
        if self.loginAwaitingConfirmation:
            self.job.finish_login.set()
            self._awaiting_confirmation = False
            self.inform("Đang lưu và kiểm tra phiên Chrome…")
        elif self.job:
            self.job.cancel.set()
            self.inform("Đang đóng cửa sổ đăng nhập…")
        elif self.accounts:
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
        self.job.confirmation.connect(self._confirmation)
        self.job.finished.connect(self._finished)
        self.job.start()
        self.inform("Đang mở ChatGPT trong Chrome riêng. Đăng nhập trực tiếp ở cửa sổ vừa mở…")

    @Slot(str)
    def checkAccount(self, account_id):
        if not self._available():
            return
        self._start_check(account_id)

    @Slot()
    def refreshAccounts(self):
        if self.job or self.bridge.busy:
            return
        due = self.store.due_accounts()
        if due:
            self._start_check(due[0])

    def _start_check(self, account_id):
        self.store.probe_started(account_id)
        self.job = WebLoginJob(self.store.get(account_id), self.store.root, self, check_only=True)
        self.job.finished.connect(self._finished)
        self.job.start()
        self.inform("Đang kiểm tra phiên tài khoản…")

    def finishProbeBeforeConversion(self, folder):
        if not self.job or not self.job.check_only:
            return False
        self._after_probe = folder
        self.job.cancel.set()
        self.inform("Đang kết thúc kiểm tra phiên để chuyển đổi bài…")
        return True

    @Slot(bool)
    def _confirmation(self, value):
        self._awaiting_confirmation = value
        self.changed.emit()

    @Slot()
    def _finished(self):
        job, self.job = self.job, None
        self._awaiting_confirmation = False
        if job.cancel.is_set() or job.error_code == "busy":
            self._restore_error()
            self.inform("Đã dừng kiểm tra; phiên tài khoản được giữ." if job.cancel.is_set()
                        else "Profile đang được sử dụng; tool sẽ kiểm tra khi rảnh.")
        elif job.error:
            self._error = True
            self._error_code = job.error_code
            self.store.login_error(job.account["id"], job.error_code, job.error)
            self.inform(job.error)
        elif job.result and job.result.get("ready"):
            self.store.observe(job.account["id"], job.result.get("plan", "unknown"), identity=job.result)
            if job.result.get("quota_limited"):
                self.store.login_error(job.account["id"], "limit", "Đã đăng nhập nhưng web đang báo hết lượt. Chờ hạn mức được cấp lại; không cần đăng nhập lại.",
                                       retry_after_seconds=job.result.get("retry_after_seconds"))
            self._error = False
            self._error_code = ""
            self.inform("Đã kiểm tra phiên tài khoản." if job.check_only else "Đã đăng nhập và lưu phiên web.")
        else:
            self.inform("Chưa xác nhận đăng nhập mới. Bấm Đăng nhập để tiếp tục.")
        if job.resume and job.result and job.result.get("ready") and not job.cancel.is_set():
            # User requested recovery of this job; continue only after the
            # visible login confirms the same saved browser profile.
            QTimer.singleShot(0, lambda folder=job.request_folder: self._continue_request(folder))
        job.deleteLater()
        if job.check_only and self._after_probe:
            folder, self._after_probe = self._after_probe, ""
            QTimer.singleShot(0, lambda: self._continue_request(folder))

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

    @Slot(str)
    def _succeeded(self, account_id):
        self.store.conversion_succeeded(account_id)
        self._restore_error()
        self.changed.emit()

    @Slot(str, str, str)
    def _failed(self, account_id, code, message):
        self.store.login_error(account_id, code, message)
        if code in {"login", "verification", "auth_response"}:
            self.store.begin_login(account_id)
        self._restore_error()
        self.inform(message)

    def conversionAccount(self, folder=""):
        journal = Path(folder) / "browser-job.json" if folder else None
        if journal and journal.is_file():
            record = json.loads(journal.read_text(encoding="utf-8"))
            from .browser_dispatch import unsent

            if not unsent(record):
                return self.store.get(record["account_id"])
        return self.store.preferred()

    def conversionAccounts(self, folder):
        journal = Path(folder) / "browser-job.json"
        if journal.is_file():
            record = json.loads(journal.read_text(encoding="utf-8"))
            from .browser_dispatch import unsent

            if not unsent(record):
                return [self.store.get(record["account_id"])]
        return self.store.candidates()

    @Slot()
    def openUsage(self):
        self.signIn(self.activeId)

    def shutdown(self):
        self._health_timer.stop()
        self._after_probe = ""
        if self.job:
            self.job.cancel.set()
            self.job.wait()
