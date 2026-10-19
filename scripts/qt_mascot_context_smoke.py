"""Qt right-click mascot menu and eye-off header; isolated app windows only."""

import json
import tempfile
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlProperty
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump, until


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    reports = Path('reports/rc100/mascot-context')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-mascot-menu-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')

        def c(name):
            return control(companion, name)

        def click(item):
            QTest.mouseClick(item.window(), Qt.LeftButton, Qt.NoModifier,
                             item.mapToScene(QPointF(item.width()/2, item.height()/2)).toPoint())
            pump(100)

        def open_menu():
            body = c('mascotToggle')
            before = (companion.x(), companion.y(), companion.property('collapsed'))
            QTest.mouseClick(companion, Qt.RightButton, Qt.NoModifier,
                             body.mapToScene(QPointF(body.width()/2, body.height()/2)).toPoint())
            until(lambda: c('mascotContextMenu').property('visible'))
            assert (companion.x(), companion.y(), companion.property('collapsed')) == before
            for name in ('mascotContextSettings', 'mascotContextHide'):
                assert c(name).isVisible() and c(name).isEnabled()
            popup = c('mascotContextHide').window()
            rect = popup.screen().availableGeometry()
            assert rect.contains(popup.geometry()), (rect, popup.geometry())
            return popup

        try:
            companion.setProperty('collapsed', True)
            bridge.showCompanion(companion)
            pump(200)
            popup = open_menu()
            assert popup.grabWindow().save(str(reports/'context-menu.png'))
            assert QQmlProperty(c('mascotContextSettings'), 'icon.source').read().toString().endswith('settings-active.png')
            assert QQmlProperty(c('mascotContextHide'), 'icon.source').read().toString().endswith('eye-off.svg')
            click(c('mascotContextSettings'))
            until(lambda: root.property('page') == 'settings')
            assert control(root, 'settingsPage').property('activeTab') == 3
            for collapsed in (True, False):
                companion.setProperty('collapsed', collapsed)
                bridge.showCompanion(companion)
                pump(200)
                open_menu()
                click(c('mascotContextHide'))
                assert not companion.isVisible() and not c('mascotContextMenu').property('visible')
                control(root, 'openCompanion').clicked.emit()
                pump(200)
                assert companion.isVisible()
            companion.setProperty('collapsed', True)
            pump(120)
            click(c('mascotToggle'))
            assert not companion.property('collapsed'), 'Left click still opens the controls'
            hide = c('hideCompanion')
            assert hide.property('imageSource').toString().endswith('eye-off.svg') and not hide.property('glyph')
            assert companion.grabWindow().save(str(reports/'header-eye-off.png'))
            click(hide)
            assert not companion.isVisible()
            assert not warnings, warnings
            result = dict(status='passed', qml_warnings=warnings, checks=[
                'Right click opens two icon actions without moving or expanding mascot',
                'Gear opens Mascot settings; eye-off hides compact/expanded mascot',
                'Native popup stays on screen; sidebar can reopen hidden mascot',
                'Header uses the same eye-off icon; normal left click still works'])
            (reports/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                           bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                           bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                worker.shutdown()
            companion.setProperty('disposing', True)
            companion.hide()
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
