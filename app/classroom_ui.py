"""Desktop controls for the classroom process and saved reports."""

import base64
import io
import socket

import psutil
from PySide6.QtCore import Property, QObject, QThread, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QGuiApplication

from . import analytics
from .classroom_server import ClassroomRuntime
from .readiness import assess


class NetworkJob(QThread):
    result = Signal(object, str)

    def __init__(self, action, parent):
        super().__init__(parent)
        self.action = action

    def run(self):
        try:
            self.result.emit(self.action(), "")
        except Exception as exc:
            self.result.emit(None, str(exc))


class ClassroomBridge(QObject):
    changed = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        bridge.changed.connect(self.changed)
        self.runtime = None
        self.worker = None
        self._result = None
        self._pending = None
        self._message = "Chọn bài đã duyệt để bắt đầu lớp."
        self._network_notice = ""
        self._state = {}
        self._url = self._qr = ""
        self._report = {}
        self._sessions = analytics.list_sessions(bridge.library.directory)
        self.timer = QTimer(self)
        self.timer.setInterval(900)
        self.timer.timeout.connect(self.poll)

    @Property("QVariantList", notify=changed)
    def interfaces(self):
        result = []
        for name, addresses in psutil.net_if_addrs().items():
            if not psutil.net_if_stats().get(name) or not psutil.net_if_stats()[name].isup:
                continue
            for address in addresses:
                if address.family == socket.AF_INET and not address.address.startswith("169.254."):
                    result.append({"name": f"{name} · {address.address}", "host": address.address})
        if not any(r["host"] == "127.0.0.1" for r in result):
            result.append({"name": "Chỉ thử trên máy · 127.0.0.1", "host": "127.0.0.1"})
        return result

    @Property(bool, notify=changed)
    def running(self):
        return bool(self.runtime and self.runtime.process and self.runtime.process.is_alive())

    @Property(bool, notify=changed)
    def busy(self):
        return self.worker is not None or self.bridge.busy

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Property(str, notify=changed)
    def joinUrl(self):
        return self._url

    @Property(str, notify=changed)
    def qrImage(self):
        return self._qr

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self._state

    @Property("QVariantList", notify=changed)
    def sessions(self):
        return self._sessions

    @Property("QVariantMap", notify=changed)
    def selectedReport(self):
        return self._report

    @Slot(str, str, int, str, str)
    def start(self, title, mode, size, host, resume):
        if self.running or self.bridge.busy or self.worker:
            return
        if resume:
            # A resumed session teaches its immutable snapshot, even if the
            # source lesson has since changed or is not open in the workspace.
            current = {}
        else:
            lesson = self.bridge.lesson
            if not lesson or not lesson.get("id"):
                self._message = "Mở một bài học trước khi bắt đầu lớp."
                self.changed.emit()
                return
            current = self.bridge.library.get(lesson["id"])
            if current["revision"] != lesson["revision"]:
                self._message = "Bài vừa được sửa. Mở lại bài rồi kiểm tra bản chuẩn bị."
                self.changed.emit()
                return
            checks = assess(current, self.bridge.library.directory, self.bridge._voices,
                            self.bridge.voiceSettings, self.bridge.voiceSettings["rate"])
            if not checks["prepared_ready"]:
                self._message = "Bài chưa được chốt để dạy. Duyệt đủ nội dung, mở Chuẩn bị lên lớp và bấm Chốt bản chuẩn bị."
                self.changed.emit()
                return
        runtime = ClassroomRuntime(self.bridge.library.directory)
        self.runtime = runtime
        self._message = "Đang mở lớp…"
        def created(info):
            import qrcode
            self._url = f"http://{info['host']}:{info['port']}/#join={info['join']}&session={info['session_id']}"
            stream = io.BytesIO()
            qrcode.make(self._url).save(stream, format="PNG")
            self._qr = "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode()
            self._state = runtime.request()
            self._network_notice = ("Địa chỉ lớp đã đổi. Phát QR mới; học sinh dùng mã khôi phục cá nhân để vào lại đúng chỗ. "
                                    if info.get("network_changed") else "")
            self._message = self._network_notice + "Lớp đã mở. Học sinh dùng cùng Wi-Fi và quét QR."
            self.timer.start()
            self.refreshReports()
            self.changed.emit()
        self.bridge.launch(lambda: runtime.start(current, {"title": title, "mode": mode, "size": size, "host": host, "resume": resume}), created)
        self.changed.emit()

    @Slot()
    def poll(self):
        if not self.running or self.worker or self.bridge.busy:
            return
        self._begin_request(None)

    def _begin_request(self, payload):
        self._result = None
        self.worker = NetworkJob(lambda: self.runtime.request(payload), self)
        self.worker.result.connect(self._receive)
        self.worker.finished.connect(self._finish)
        self.worker.start()
        self.changed.emit()

    @Slot(object, str)
    def _receive(self, result, error):
        self._result = result, error

    @Slot()
    def _finish(self):
        if self.worker is None:
            return
        result, error = self._result or (None, "Chưa nhận được phản hồi.")
        if error:
            self._message = error
        else:
            self._state = result
            self._message = (self._network_notice + "Đang cập nhật phản hồi của lớp." if result["status"] == "active"
                             else "Tiết học đã kết thúc. Xem kết quả trong Báo cáo.")
        self.worker.deleteLater()
        self.worker = None
        self.changed.emit()
        if self._pending is not None:
            payload, self._pending = self._pending, None
            self._begin_request(payload)
        if result and result["status"] == "ended":
            self.timer.stop()
            self.refreshReports()

    @Slot(str, int, str, bool)
    def openQuestion(self, question_id, duration, language, recheck):
        payload = {"action": "open", "question_id": question_id, "duration": duration, "language": language}
        if recheck:
            payload["recheck_of"] = (self._state.get("round") or {}).get("id")
        self._action(payload)

    @Slot(str)
    def action(self, action):
        self._action({"action": action})

    def _action(self, payload):
        if not self.running:
            self._message = "Mở lớp trước khi dùng thao tác này."
            self.changed.emit()
            return
        if self.worker:
            self._pending = payload
        else:
            self._begin_request(payload)

    @Slot()
    def disconnect(self):
        self.timer.stop()
        self._pending = None
        if self.worker:
            self.worker.wait(4000)
            self.worker.result.disconnect(self._receive)
            self.worker.finished.disconnect(self._finish)
            self.worker.deleteLater()
            self.worker = None
            self._result = None
        if self.runtime:
            self.runtime.stop()
        self.runtime = None
        self._state = {}
        self._qr = self._url = ""
        self._network_notice = ""
        self._message = "Đã ngắt máy chủ. Phiên chưa kết thúc có thể mở lại từ Báo cáo."
        self.changed.emit()
        self.refreshReports()

    @Slot()
    def copyUrl(self):
        QGuiApplication.clipboard().setText(self._url)
        self._message = "Đã sao chép liên kết tham gia."
        self.changed.emit()

    @Slot()
    def openStudentPage(self):
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))

    @Slot()
    def refreshReports(self):
        self._sessions = analytics.list_sessions(self.bridge.library.directory)
        self.changed.emit()

    @Slot(str)
    def openReport(self, session_id):
        try:
            self._report = analytics.report(self.bridge.library.directory, session_id)
            self.changed.emit()
        except Exception as exc:
            self._message = str(exc)
            self.changed.emit()

    @Slot(str)
    def exportReport(self, url):
        try:
            path = analytics.export_csv(self.bridge.library.directory, self._report["id"], QUrl(url).toLocalFile())
            self._message = "Đã xuất CSV: " + str(path)
        except Exception as exc:
            self._message = str(exc)
        self.changed.emit()

    @Slot(str)
    def exportResponses(self, url):
        try:
            path = analytics.export_response_csv(self.bridge.library.directory, self._report["id"], QUrl(url).toLocalFile())
            self._message = "Đã xuất từng phản hồi: " + str(path)
        except Exception as exc:
            self._message = str(exc)
        self.changed.emit()

    @Slot(str)
    def deleteReport(self, session_id):
        if self.running and self._state.get("session_id") == session_id:
            self._message = "Ngắt máy chủ trước khi xóa phiên này."
        else:
            try:
                analytics.delete_session(self.bridge.library.directory, session_id)
                self._report = {}
            except Exception as exc:
                self._message = str(exc)
        self.refreshReports()
