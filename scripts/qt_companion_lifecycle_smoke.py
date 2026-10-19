"""Real Qt close/minimize/hide semantics with a disposable library."""

import json
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump, until


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc82/lifecycle')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-lifecycle-', ignore_cleanup_errors=True) as directory:
        library = Library(Path(directory))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda entries: warnings.extend(map(str, entries)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(RESOURCE_ROOT / 'qml/Main.qml')
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')
        watchdog = QTimer()
        watchdog.setSingleShot(True)
        timed_out = []
        watchdog.timeout.connect(lambda: (timed_out.append(True), app.quit()))
        try:
            until(lambda: bridge._catalog.worker is None)
            bridge.showCompanion(companion)
            companion.setProperty('collapsed', False)
            pump(120)
            root.showMinimized()
            pump(150)
            assert companion.isVisible(), 'Minimize must keep the teaching companion visible'
            companion.hide()
            pump(100)
            assert not companion.isVisible() and root.isVisible(), 'Hide affects only the companion'
            root.showNormal()
            bridge.showCompanion(companion)
            pump(120)
            # Existing busy-close protection must still retain both windows.
            bridge._busy = True
            bridge.changed.emit()
            assert not root.close()
            pump(100)
            assert root.isVisible() and companion.isVisible()
            bridge._busy = False
            bridge.changed.emit()
            # A visible independent tool window must not keep the event loop
            # alive after the teacher closes the main window.
            watchdog.start(5000)
            started = time.monotonic()
            QTimer.singleShot(20, root.close)
            app.exec()
            watchdog.stop()
            assert not timed_out, 'Closing BiliClass left the companion/event loop running'
            assert not companion.isVisible() and not root.isVisible()
            assert companion.property('disposing')
            assert not warnings, warnings
            result = dict(status='passed', close_seconds=round(time.monotonic() - started, 3),
                          minimize_keeps_mascot=True, hide_is_local=True, busy_close_guard=True,
                          close_exits_with_open_panel=True, qml_warnings=warnings)
            (report / 'result.json').write_text(json.dumps(result), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            watchdog.stop()
            companion.setProperty('disposing', True)
            companion.hide()
            root.hide()
            for worker in (bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog, bridge.browserAI,
                           bridge.english_reader, bridge.narration_preparation, bridge.classroom, bridge.voice_controls,
                           bridge._narration_preferences, bridge._companion_preferences):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
