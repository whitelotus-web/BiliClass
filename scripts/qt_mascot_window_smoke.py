"""Check native Windows visibility/z-order; Qt's visible property alone is insufficient."""

import json
import logging
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import win32con
import win32gui
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import control, pump

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    out = Path("reports/rc69/mascot")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bcl-topmost-", ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder) / "data")
        bridge = Bridge(library)
        assert bridge.mascotSettings["always_on_top"] is True
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(RESOURCE_ROOT / "qml/Main.qml")
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        companion = control(window, "companionWindow")
        cover = None

        def native_visible():
            handle = int(companion.winId())
            return bool(win32gui.IsWindowVisible(handle) and not win32gui.IsIconic(handle))

        def topmost():
            return bool(
                win32gui.GetWindowLong(int(companion.winId()), win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST
            )

        try:
            bridge.showCompanion(companion)
            pump(180)
            assert companion.transientParent() is None
            assert native_visible() and topmost()
            hwnd = int(window.winId())
            for _ in range(3):
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                pump(180)
                assert native_visible() and topmost(), "Native minimize hid the companion"
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                pump(100)
            engine.loadData(
                b'import QtQuick\nWindow { visible: true; width: 800; height: 600; color: "#dce6f3"; title: "Disposable foreground window" }',
                QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/MascotCoverSmoke.qml")),
            )
            cover = engine.rootObjects()[-1]
            cover.showFullScreen()
            pump(180)
            assert native_visible() and topmost()
            z_order = []
            win32gui.EnumWindows(lambda handle, _: z_order.append(handle), None)
            assert z_order.index(int(companion.winId())) < z_order.index(int(cover.winId()))
            cover.hide()
            companion.setProperty("collapsed", False)
            pump(100)
            companion.findChild(QObject, "hideCompanion").clicked.emit()
            pump(100)
            assert not native_visible()
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            pump(100)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            pump(100)
            assert not native_visible(), "Explicit hide must survive minimize/restore"
            window.setProperty("page", "settings")
            control(window, "settingsTab3").clicked.emit()
            pump(150)
            check = control(window, "mascotAlwaysOnTop")
            assert check.property("checked")
            for enabled in (False, True):
                check.setProperty("checked", enabled)
                control(window, "saveMascot").clicked.emit()
                pump(250)
                assert bridge.mascotSettings["always_on_top"] == enabled
                assert native_visible() and topmost() == enabled
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                pump(150)
                assert native_visible(), "The companion must remain independent even with topmost off"
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                pump(100)
            assert window.grabWindow().save(str(out / "always-on-top-setting.png"))
            assert not warnings, warnings
            result = {
                "status": "passed",
                "qml_warnings": warnings,
                "checks": [
                    "default topmost",
                    "no transient owner",
                    "native minimize/restore repeated",
                    "z-order above a normal full-screen window",
                    "explicit hide retained",
                    "checkbox save toggles native topmost style",
                    "minimize with topmost off",
                ],
                "scope": "Current Windows desktop; not exclusive GPU fullscreen or a secure desktop",
            }
            (out / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps(result), flush=True)
        finally:
            if cover:
                cover.hide()
            companion.hide()
            window.hide()
            for worker in (
                bridge.libraryThumbnails,
                bridge.slidePreview,
                bridge._catalog,
                bridge.browserAI,
                bridge.english_reader,
                bridge.narration_preparation,
                bridge.classroom,
                bridge.voice_controls,
            ):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
            logging.shutdown()


if __name__ == "__main__":
    main()
