"""Rapid mascot toggles keep the native window and mascot anchor stable."""
import json
import sys
import tempfile
import time
from pathlib import Path

import win32gui
from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump, until


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT / 'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    reports = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/companion-toggle')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-toggle-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')
        mascot = control(root, 'mascotToggle')
        frames, samples, scenarios = [], [], []
        recording = False

        def capture():
            if not recording:
                return
            point = mascot.mapToGlobal(QPointF())
            frames.append(dict(time=time.perf_counter(), x=point.x(), y=point.y(),
                               visible=win32gui.IsWindowVisible(int(companion.winId())),
                               native_rect=win32gui.GetWindowRect(int(companion.winId())),
                               size=[companion.width(), companion.height()]))

        companion.afterAnimating.connect(capture)

        def tap():
            QTest.mouseClick(companion, Qt.LeftButton, Qt.NoModifier,
                             mascot.mapToScene(QPointF(mascot.width()/2, mascot.height()/2)).toPoint())

        try:
            until(lambda: bridge._catalog.worker is None)
            area = app.primaryScreen().availableGeometry()
            for theme in ('light', 'dark'):
                bridge.setApplicationTheme(theme)
                for side in ('left', 'right'):
                    for vertical in ('top', 'bottom'):
                        companion.setProperty('collapsed', True)
                        pump(180)
                        extent = companion.property('mascotExtent')
                        anchor_x = area.left()+20 if side == 'left' else area.right()-extent-20
                        anchor_y = area.top()+20 if vertical == 'top' else area.bottom()-extent-20
                        bridge.saveMascotLocation(anchor_x, anchor_y)
                        bridge.showCompanion(companion)
                        pump(180)
                        handle = int(companion.winId())
                        native_rect = win32gui.GetWindowRect(handle)
                        frames.clear()
                        recording = True
                        for delay in (20, 45, 90):
                            for _ in range(8):
                                tap()
                                pump(delay)
                        pump(220)
                        recording = False
                        assert companion.property('collapsed'), 'Every rapid click must toggle exactly once'
                        assert int(companion.winId()) == handle and all(frame['visible'] for frame in frames)
                        drift = max(max(abs(frame['x']-anchor_x), abs(frame['y']-anchor_y)) for frame in frames)
                        scenarios.append(dict(theme=theme, side=side, vertical=vertical, frames=len(frames), max_anchor_drift=drift))
                        samples.extend(dict(scenario=len(scenarios)-1, **frame) for frame in frames)
                        (reports / 'samples.json').write_text(json.dumps(samples), encoding='utf-8')
                        assert drift <= 2, scenarios[-1]
                        assert all(tuple(frame['native_rect']) == native_rect for frame in frames), 'Toggling must not move/resize the native surface and expose its old texture'
                        assert companion.mask().boundingRect().width() == extent
                        assert companion.mask().boundingRect().height() == extent
                        origin = win32gui.ClientToScreen(handle, (0, 0))
                        ratio = companion.devicePixelRatio()
                        def native_hit(item):
                            point = item.mapToScene(QPointF(item.width()/2, item.height()/2))
                            return win32gui.WindowFromPoint((origin[0] + round(point.x()*ratio), origin[1] + round(point.y()*ratio)))
                        assert native_hit(mascot) == handle, 'The mini mascot must still receive native input'
                        assert native_hit(control(root, 'companionMenu')) != handle, 'The hidden panel must let native input through'
                        tap()
                        pump(180)
                        assert control(root, 'companionMenu').isVisible()
                        assert native_hit(control(root, 'companionMenu')) == handle
                        assert companion.grabWindow().save(str(reports / f'{theme}-{side}-{vertical}.png'))
                        control(root, 'collapseCompanionPanel').clicked.emit()
                        pump(180)
                        assert companion.property('collapsed') and companion.mask().boundingRect().width() == extent
            companion.setProperty('collapsed', False)
            pump(180)
            companion.hide()
            companion.setProperty('collapsed', True)
            pump(20)
            assert companion.property('panelOpacity') == 0
            bridge.showCompanion(companion)
            pump(80)
            assert companion.mask().boundingRect().width() == companion.property('mascotExtent')
            assert not control(root, 'companionMenu').isVisible(), 'Reopening the mini mascot must not flash the hidden panel'
            assert not warnings, warnings
            result = dict(status='passed', scenarios=scenarios, qml_warnings=warnings,
                          rapid_clicks=24*len(scenarios), native_window_retained=True,
                          native_surface_unchanged=True, collapsed_panel_input_passes_through=True,
                          scope='Current Windows screens; Qt mouse input targets only the disposable mascot')
            (reports / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            recording = False
            companion.setProperty('disposing', True)
            companion.hide()
            root.hide()
            for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                           bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                           bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
