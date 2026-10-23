"""Verify normal startup/taskbar boundaries without changing display settings."""

import ctypes
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import win32api
import win32gui
from PySide6.QtCore import QCoreApplication, QEvent, QPointF, QRect, QSize, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from app.window_geometry import WindowGeometry
from app.windows_identity import configure_window
from scripts.qt_result_preview_mascot_smoke import control, pump, until


def main():
    is_hung = ctypes.windll.user32.IsHungAppWindow
    is_hung.argtypes = [ctypes.c_void_p]
    is_hung.restype = ctypes.c_int
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    scale = os.environ.get('QT_SCALE_FACTOR', '1')
    report = Path('reports/rc161/window') / scale
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-window-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        configure_window(root)
        geometry = WindowGeometry(root, QSize(1366, 850))
        samples = []

        def verify(label, area):
            pump(180)
            assert root.windowState() == Qt.WindowNoState
            frame = root.frameGeometry()
            assert area.adjusted(-1, -1, 1, 1).contains(frame), (label, area, frame)
            work = win32api.GetMonitorInfo(win32api.MonitorFromWindow(int(root.winId())))['Work']
            native = win32gui.GetWindowRect(int(root.winId()))
            assert (native[0] >= work[0]-2 and native[1] >= work[1]-2
                    and native[2] <= work[2]+2 and native[3] <= work[3]+2), (native, work)
            samples.append({'label': label, 'frame': frame.getRect(), 'area': area.getRect(),
                            'native_frame': native, 'native_work': work,
                            'minimum': (root.minimumWidth(), root.minimumHeight())})

        try:
            until(root.isVisible)
            actual = root.screen().availableGeometry()
            verify('cold-start', actual)
            root.setProperty('page', 'settings')
            pump(100)
            # Emulate a 1366x768 laptop's work area in this process only. The
            # real Windows monitor, scale setting and taskbar remain untouched.
            virtual = QRect(actual.x(), actual.y(), min(actual.width(), round(1366/float(scale))),
                            min(actual.height(), round(728/float(scale))))
            with patch.object(geometry, '_area', return_value=virtual):
                geometry._initial = True
                geometry.fit()
                verify('laptop-normal', virtual)
                before = root.size()
                for index in range(3):
                    root.showMaximized()
                    until(lambda: root.windowState() == Qt.WindowMaximized)
                    pump(60)
                    root.showNormal()
                    until(lambda: root.windowState() == Qt.WindowNoState)
                    verify(f'restore-{index}', virtual)
                    assert root.size() == before, (root.size(), before)
                assert root.grabWindow().save(str(report/'normal-settings.png'))
                control(root, 'settingsPage').setProperty('activeTab', 2)
                pump(120)
                scroll = control(root, 'settingsContentScroll').property('contentItem')
                scroll.setProperty('contentY', max(0, scroll.property('contentHeight')-scroll.height()))
                pump(100)
                save = control(root, 'saveMultilingualVoice')
                point = save.mapToScene(QPointF())
                assert save.isVisible() and point.y() >= 0 and point.y()+save.height() <= root.height(), (
                    point.y(), save.height(), root.height())
                assert root.grabWindow().save(str(report/'normal-voice-settings.png'))
            assert not warnings, warnings
            value = {'status': 'passed', 'scale': scale, 'dpr': root.devicePixelRatio(), 'samples': samples,
                     'qml_warnings': warnings, 'display_settings_changed': False,
                     'responsive': not bool(is_hung(int(root.winId())))}
            (report/'result.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
            print(json.dumps({'status': 'passed', 'scale': scale, 'samples': len(samples)}), flush=True)
        finally:
            geometry._timer.stop()
            control(root, 'companionWindow').setProperty('disposing', True)
            root.hide()
            for name in ('libraryThumbnails', 'googleSettings', '_library_preferences', 'slidePreview', '_catalog',
                         'browserAI', 'english_reader', 'narration_preparation', 'narrationPreferences',
                         '_companion_preferences', 'classroom', 'voice_controls', 'inputDocuments'):
                getattr(bridge, name).shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
