"""Exercise the real Qt projector window on the attached secondary screen."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QEventLoop, QObject, QTimer, QUrl
from PySide6.QtGui import QGuiApplication, QWindow
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def pause(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def main():
    application = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    screens = QGuiApplication.screens()
    if len(screens) < 2:
        raise RuntimeError("An attached secondary Windows display is required for this check.")
    secondary = next(screen for screen in screens if screen != QGuiApplication.primaryScreen())
    with tempfile.TemporaryDirectory(prefix="biliclass-display-", ignore_cleanup_errors=True) as temporary:
        library = Library(temporary)
        try:
            lesson = library.create("Bài kiểm tra màn hình", "Liên môn", "THPT", "11", [("Đoạn", "Hãy thảo luận theo nhóm.")])
            library.edit_segment(lesson["id"], lesson["segments"][0]["id"],
                                 "Hãy thảo luận theo nhóm.", "Discuss in groups.", True)
            bridge = Bridge(library)
            bridge.openLesson(lesson["id"])
            engine = QQmlApplicationEngine()
            warnings = []
            engine.warnings.connect(lambda items: warnings.extend(str(item) for item in items))
            engine.rootContext().setContextProperty("bridge", bridge)
            engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
            assert engine.rootObjects(), warnings
            root = engine.rootObjects()[0]
            root.resize(1366, 768)
            projector = root.findChild(QObject, "projectorWindow")
            assert projector is not None
            target_index = screens.index(secondary)
            bridge.showProjector(projector, target_index)
            pause(600)
            assert (projector.isVisible() and projector.visibility() == QWindow.Visibility.FullScreen
                    and projector.screen() == secondary)
            target = Path(__file__).resolve().parents[1] / "reports/app/projector-secondary.png"
            assert projector.grabWindow().save(str(target))
            assert not warnings, warnings
            result = {"status": "passed", "screens": [
                {"name": item.name(), "geometry": [item.geometry().x(), item.geometry().y(),
                 item.geometry().width(), item.geometry().height()], "dpr": item.devicePixelRatio()}
                for item in screens], "projector_screen": secondary.name(), "full_screen": True,
                "qml_warnings": [], "scope": "current two-display Windows desk, not a school projector or Presenter View"}
        finally:
            if "projector" in locals():
                projector.hide()
            if "root" in locals():
                root.hide()
            if "bridge" in locals():
                bridge.classroom.disconnect()
                for handler in tuple(bridge.logger.handlers):
                    if str(temporary).casefold() in getattr(handler, "baseFilename", "").casefold():
                        bridge.logger.removeHandler(handler)
                        handler.close()
            if "engine" in locals():
                engine.deleteLater()
                pause(100)
            library.close()
    (Path(__file__).resolve().parents[1] / "reports/app/displays.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    del application


if __name__ == "__main__":
    main()
