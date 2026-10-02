"""Smoke-test supplied navigation icons and the saved mascot's visible launcher."""

import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QEventLoop, QObject, QPoint, QPointF, Qt, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def pump(ms=150):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def main():
    resource_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RESOURCE_ROOT
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    with tempfile.TemporaryDirectory(prefix="biliclass-nav-", ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        library.create("Bài kiểm tra", "Môn tự chọn", "THPT", "10", [("Mở đầu", "Nội dung mẫu")])
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda entries: warnings.extend(map(str, entries)))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(QUrl.fromLocalFile(str(resource_dir / "qml" / "Main.qml")))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        window.setProperty("page", "settings")
        pump(350)
        companion = window.findChild(QObject, "companionWindow")
        launcher = window.findChild(QObject, "openCompanion")
        assert companion and launcher
        assert launcher.isVisible() and not companion.isVisible()

        bridge.saveMascotPreferences("Lumi", True, 110, "right", False, True, True, True)
        pump()
        assert companion.isVisible(), "Mascot should appear as soon as visible settings are saved"
        assert bridge.settings["mascot"] == "Lumi"
        assert companion.property("collapsed") and companion.width() <= 130
        assert not window.findChild(QObject, "companionMenu").isVisible()
        reports = RESOURCE_ROOT.parent / "reports" / "app"
        reports.mkdir(parents=True, exist_ok=True)
        floating = companion.grabWindow()
        assert floating.pixelColor(0, 0).alpha() == 0, "Collapsed window must be transparent"
        assert floating.save(str(reports / "mascot-floating.png"))
        start_x, start_y = companion.x(), companion.y()
        center = QPoint(companion.width() // 2, companion.height() // 2)
        QTest.mousePress(companion, Qt.LeftButton, pos=center)
        QTest.mouseMove(companion, center + QPoint(-90, -70))
        QTest.mouseRelease(companion, Qt.LeftButton, pos=center + QPoint(-90, -70))
        pump(200)
        assert companion.property("collapsed"), "Dragging must not open the menu"
        assert companion.x() < start_x - 40 and companion.y() < start_y - 30, "Mascot should follow the pointer"
        saved_location = library.setting("mascot_location", {})
        assert saved_location == {"x": companion.x(), "y": companion.y()}, saved_location
        dragged_x, dragged_y = companion.x(), companion.y()
        QTest.mouseClick(companion, Qt.LeftButton, pos=QPoint(companion.width() // 2, companion.height() // 2))
        pump(200)
        assert not companion.property("collapsed") and window.findChild(QObject, "companionMenu").isVisible()
        assert companion.width() >= 300
        mascot = window.findChild(QObject, "mascotToggle")
        assert abs(companion.x() + mascot.x() - dragged_x) <= 1
        assert abs(companion.y() + mascot.y() - dragged_y) <= 1
        assert not companion.property("hasResponse"), "The menu should open without an empty response panel"
        assert companion.grabWindow().save(str(reports / "mascot-menu.png"))
        explain = window.findChild(QObject, "companionExplain")
        explain_center = explain.mapToScene(QPointF(explain.width() / 2, explain.height() / 2)).toPoint()
        QTest.mouseClick(companion, Qt.LeftButton, pos=explain_center)
        pump(200)
        assert companion.property("hasResponse") and "duyệt" in bridge.teaching.response["text"]
        assert companion.grabWindow().save(str(reports / "mascot-menu-response.png"))
        extent = companion.property("mascotExtent")
        expanded_center = QPoint(companion.width() - extent // 2, companion.height() - extent // 2)
        QTest.mousePress(companion, Qt.LeftButton, pos=expanded_center)
        QTest.mouseMove(companion, expanded_center + QPoint(-35, -25))
        QTest.mouseRelease(companion, Qt.LeftButton, pos=expanded_center + QPoint(-35, -25))
        pump(150)
        assert not companion.property("collapsed"), "Dragging an open mascot must keep its controls open"
        dragged_x, dragged_y = companion.x() + mascot.x(), companion.y() + mascot.y()
        assert library.setting("mascot_location", {}) == {"x": dragged_x, "y": dragged_y}
        QTest.mouseClick(companion, Qt.LeftButton, pos=QPoint(companion.width() - extent // 2, companion.height() - extent // 2))
        pump(200)
        assert companion.property("collapsed") and companion.width() <= 130
        assert abs(companion.x() - dragged_x) <= 1 and abs(companion.y() - dragged_y) <= 1
        companion.hide()
        bridge.showCompanion(companion)
        pump(150)
        assert abs(companion.x() - dragged_x) <= 1 and abs(companion.y() - dragged_y) <= 1
        bridge.saveMascotPreferences("Milo", False, 110, "left", True, True, True, True)
        pump()
        assert not companion.isVisible() and not launcher.isVisible()
        assert library.setting("mascot_location", {}) == {}, "Changing the corner should clear the dragged position"
        bridge.saveMascotPreferences("Milo", True, 110, "right", False, True, True, True)
        pump()
        assert companion.isVisible() and launcher.isVisible()
        area = QGuiApplication.primaryScreen().availableGeometry()
        bridge.saveMascotLocation(area.left() + 50, area.top() + 20)
        bridge.showCompanion(companion)
        pump(150)
        QTest.mouseClick(companion, Qt.LeftButton, pos=center)
        pump(150)
        assert not companion.property("mascotAtBottom"), "Menu should open below a mascot near the top edge"
        assert abs(companion.x() + mascot.x() - area.left() - 50) <= 1
        assert abs(companion.y() + mascot.y() - area.top() - 20) <= 1
        reset = window.findChild(QObject, "resetCompanionPosition")
        reset_center = reset.mapToScene(QPointF(reset.width() / 2, reset.height() / 2)).toPoint()
        QTest.mouseClick(companion, Qt.LeftButton, pos=reset_center)
        pump(150)
        assert library.setting("mascot_location", {}) == {}, "Reset should restore the configured corner"
        companion.hide()

        screenshot = RESOURCE_ROOT.parent / "reports" / "app" / "navigation-mascot.png"
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        assert window.grabWindow().save(str(screenshot))
        assert not warnings, warnings
        print("Navigation icons, transparent mascot, free drag, saved position and menu placement passed")
        window.close()
    app.quit()


if __name__ == "__main__":
    main()
