import time
import traceback
from pathlib import Path

from PySide6.QtCore import Property, QObject, QThread, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from .contracts import LevelPolicy
from .paths import RESOURCES, data_root, output_root
from .reporting import load_reports, save_report


class Worker(QThread):
    result = Signal(str, object)

    def __init__(self, name, action, parent=None):
        super().__init__(parent)
        self.name, self.action = name, action

    def run(self):
        try:
            value = self.action()
        except Exception as exc:
            value = {"status": "failed", "error": str(exc), "diagnostic": traceback.format_exc()}
        self.result.emit(self.name, value)


class Bridge(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self._reports = load_reports()
        self._busy = False
        self._message = "Sẵn sàng kiểm chứng. Mỗi kết quả được lưu trên máy."
        self._translation = ""
        self._level = 2
        self.worker = None

    @Property("QVariantMap", notify=changed)
    def reports(self):
        return self._reports

    @Property(bool, notify=changed)
    def busy(self):
        return self._busy

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Property(str, notify=changed)
    def translation(self):
        return self._translation

    @Property("QVariantMap", notify=changed)
    def policy(self):
        from dataclasses import asdict

        return asdict(LevelPolicy.for_level(self._level))

    def launch(self, name, action):
        if self._busy:
            return
        self._busy = True
        self._message = "Đang xử lý tại máy. Bạn vẫn có thể chuyển trang."
        self.worker = Worker(name, action, self)
        self.worker.result.connect(self.completed)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()
        self.changed.emit()

    @Slot(str)
    def runProbe(self, name):
        from .__main__ import PROBES, execute_probe

        if name not in PROBES:
            return
        self.launch(name, lambda: execute_probe(name))

    @Slot(str, str)
    def translate(self, text, source):
        from .probes.translation import translate_text

        if not text.strip():
            self._message = "Nhập một câu để thử dịch."
            self.changed.emit()
            return
        if len(text) > 2000:
            self._message = "Bản thử M0 nhận tối đa 2.000 ký tự mỗi lượt."
            self.changed.emit()
            return
        self.launch("translate", lambda: {"text": translate_text(text.strip(), source)})

    @Slot(str, object)
    def completed(self, name, value):
        self._busy = False
        if "error" in value:
            self._message = "Chưa hoàn tất: " + value["error"]
        elif name == "translate":
            self._translation = value["text"]
            self._message = "Bản dịch nháp đã tạo tại máy. Cần giáo viên kiểm tra trước khi sử dụng."
        else:
            self._reports = load_reports()
            self._message = "Đã lưu kết quả thử nghiệm. Xem báo cáo để biết phạm vi đã kiểm tra."
        self.changed.emit()

    @Slot(int)
    def setLevel(self, level):
        LevelPolicy.for_level(level)
        self._level = level
        self.changed.emit()

    @Slot()
    def openReports(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_root())))

    @Slot()
    def playEnglish(self):
        import winsound

        path = output_root() / "voice-en.wav"
        if not path.exists():
            self._message = "Chạy kiểm tra giọng đọc trước để tạo âm thanh thử."
        else:
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            self._message = "Đang nghe câu thử: Please explain your answer to the class."
        self.changed.emit()


def run(args):
    started = time.perf_counter()
    app = QGuiApplication([])
    app.setApplicationName("BiliClass M0")
    QQuickStyle.setStyle("Basic")
    font_path = RESOURCES / "assets" / "BeVietnamPro-Regular.ttf"
    for font in (RESOURCES / "assets").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("Be Vietnam Pro" if font_path.exists() else "Segoe UI", 10))
    engine = QQmlApplicationEngine()
    bridge = Bridge()
    engine.rootContext().setContextProperty("bridge", bridge)
    errors = []
    engine.warnings.connect(lambda warnings: errors.extend(str(item) for item in warnings))
    engine.load(QUrl.fromLocalFile(str(RESOURCES / "qml" / "Main.qml")))
    if not engine.rootObjects():
        save_report("qt", {"status": "failed", "errors": errors})
        return 1
    window = engine.rootObjects()[0]
    width, height = [int(part) for part in args.size.split("x")]
    window.setWidth(width)
    window.setHeight(height)
    window.setProperty("pageIndex", args.tab)

    def capture():
        screenshot = Path(args.screenshot) if args.screenshot else output_root() / f"qt-{width}x{height}.png"
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        saved = QQuickWindow.grabWindow(window).save(str(screenshot))
        report = {
            "status": "passed" if saved and not errors else "failed",
            "size": [width, height],
            "screenshot": str(screenshot),
            "errors": errors,
            "ready_and_capture_ms": round((time.perf_counter() - started) * 1000),
            "screen_count": len(app.screens()),
            "data_root": str(data_root()),
            "pending": ["Máy Windows sạch không Python", "DPI/máy chiếu và overlay ngoài app"],
        }
        save_report("qt", report)
        app.exit(0 if report["status"] == "passed" else 1)

    if args.smoke:
        QTimer.singleShot(1800, capture)

    def finish_worker():
        try:
            if bridge.worker and bridge.worker.isRunning():
                bridge.worker.wait(30000)
        except RuntimeError:
            pass  # A completed QThread may already have been deleted by Qt.

    app.aboutToQuit.connect(finish_worker)
    return app.exec()
