"""Disposable Qt geometry, settings navigation and hit testing; no Office/model."""

import json
import sqlite3
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPointF, QTimer, QUrl, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


class ControlBridge(Bridge):
    def __init__(self, library):
        super().__init__(library)
        self.commands = []

    @Slot(str)
    def navigatePowerPoint(self, command):
        self.commands.append(('navigate', command))

    @Slot(str)
    def companionRead(self, language):
        self.commands.append(('read', language))


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc81/companion-controls')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-controls-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        lesson = library.create('Bài đang gắn để thử điều khiển', 'Vật lý', 'THPT', '11', [('Slide 1', 'Năng lượng.')])
        bridge = ControlBridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda entries: warnings.extend(map(str, entries)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')
        def c(name):
            return control(root, name)
        try:
            until(lambda: bridge._catalog.worker is None)
            bridge.showCompanion(companion)
            companion.setProperty('collapsed', False)
            pump(150)
            assert not c('mascotCompanion').property('showSubjectBadge')
            assert not c('mascotCompanion').findChild(QObject, 'mascotSubjectBadge').isVisible()
            assert c('companionSettings').isVisible() and c('companionShortcutGuideToggle').width() == 30
            assert companion.opacity() == 1 and bridge.companionPanelOpacity == 100
            assert companion.grabWindow().save(str(report / 'unbound.png'))
            for size, pixels, width in [('small', 80, 344), ('standard', 110, 384), ('large', 150, 432)]:
                bridge.saveMascotPreferences('Milo', True, pixels, 'right', False, True, True, True)
                pump(100)
                assert companion.width() == min(width, app.primaryScreen().availableGeometry().width() - 16)
                menu = c('companionMenu')
                button = c('companionChooseLesson')
                point = button.mapToItem(menu, QPointF())
                assert abs(point.x() - (menu.width() - point.x() - button.width())) < 1
                assert button.height() == {'small': 36, 'standard': 40, 'large': 46}[size]
                gear = c('companionSettings')
                point = gear.mapToItem(menu, QPointF())
                assert point.x() > 0 and point.x() + gear.width() < menu.width()
                assert companion.grabWindow().save(str(report / (size + '.png')))
            bridge.saveMascotPreferences('Milo', True, 110, 'right', False, True, True, True)
            bridge._powerpoint_state = {'active': True, 'opened': True, 'slide': 2, 'total': 7, 'message': ''}
            bridge.powerpoint_worker = object()  # UI availability only; commands intercepted above.
            bridge.teachingSession.bind({'lesson': lesson, 'path': '', 'preview': {}, 'media': {2: ['en', 'vi', 'both']}})
            bridge.changed.emit()
            pump(150)
            audio = [c('companionRead' + language) for language in ('English', 'Vietnamese', 'Both')]
            assert all(item.isVisible() for item in audio)
            assert max(item.width() for item in audio) - min(item.width() for item in audio) <= 1, [item.width() for item in audio]
            assert max(item.mapToScene(QPointF()).y() for item in audio) - min(item.mapToScene(QPointF()).y() for item in audio) < 1
            for opacity in (100, 30):
                bridge.setCompanionPanelOpacity(opacity)
                pump(100)
                assert abs(c('companionMenu').property('color').alphaF() - opacity / 100) < .01
                assert companion.opacity() == 1 and all(item.opacity() == 1 for item in audio)
                for name in ('companionPrevious', 'companionNext', 'companionReadEnglish', 'companionReadVietnamese', 'companionReadBoth'):
                    click(companion, c(name))
                assert bridge.commands[-5:] == [('navigate', 'previous'), ('navigate', 'next'), ('read', 'en'), ('read', 'vi'), ('read', 'both')]
                assert companion.grabWindow().save(str(report / f'active-opacity-{opacity}.png'))
            click(companion, c('companionSettings'))
            pump(150)
            assert root.property('page') == 'settings' and c('settingsPage').property('activeTab') == 3
            assert bridge.teachingSession.state['lesson_id'] == lesson['id'], 'Settings must not unbind the teaching deck'
            transparency = c('companionPanelTransparency')
            transparency.setProperty('value', 0)
            transparency.moved.emit()
            assert bridge.companionPanelOpacity == 100
            assert c('settingsPage').findChild(QObject, 'companionPanelSize') is None
            assert c('settingsPage').findChild(QObject, 'mascotPosition') is None
            assert not c('mascotPreview').property('showSubjectBadge')
            assert not c('mascotPreview').findChild(QObject, 'mascotSubjectBadge').isVisible()
            for width, height in ((1366, 850), (1080, 700)):
                root.resize(width, height)
                pump(100)
                summary, toggles = c('mascotAccessorySummary'), c('mascotAlwaysOnTop')
                summary_left = summary.mapToScene(QPointF()).x()
                toggles_right = toggles.mapToScene(QPointF(toggles.width(), 0)).x()
                if c('settingsPage').property('wideMascotLayout'):
                    assert summary_left > toggles_right, 'Accessory details belong beside display choices'
                else:
                    assert summary.mapToScene(QPointF()).y() > toggles.mapToScene(QPointF(0, toggles.height())).y()
                viewport = c('settingsContentScroll').property('contentItem')
                offset = summary.mapToItem(viewport, QPointF()).y()
                viewport.setProperty('contentY', max(0, min(viewport.property('contentHeight') - viewport.height(),
                                                           viewport.property('contentY') + offset - 120)))
                pump(100)
                assert root.grabWindow().save(str(report / f'settings-{width}.png'))
            until(lambda: bridge._companion_preferences.worker is None and not bridge._companion_preferences.pending)
            assert library.setting('companion_panel_opacity', 0) == 100
            bridge.setCompanionPanelOpacity(-30)
            assert bridge.companionPanelSize == 'standard' and bridge.companionPanelOpacity == 30
            broad_refreshes, ticks = [], []
            bridge.changed.connect(lambda: broad_refreshes.append(1))
            beat = QTimer()
            beat.setInterval(10)
            beat.timeout.connect(lambda: ticks.append(time.monotonic()))
            lock = sqlite3.connect(library.directory / 'library.db')
            lock.execute('BEGIN IMMEDIATE')
            beat.start()
            try:
                for value in range(71):
                    transparency.setProperty('value', value)
                    transparency.moved.emit()
                    pump(4)
                bridge.flushCompanionAppearance()
                pump(150)
                assert bridge.companionPanelOpacity == 30 and not broad_refreshes
                assert bridge._companion_preferences.worker is not None, 'Save is waiting off the UI thread'
                assert len(ticks) > 10
                max_gap = max(b - a for a, b in zip(ticks, ticks[1:]))
                assert max_gap < .35, max_gap
            finally:
                lock.rollback()
                lock.close()
                beat.stop()
            until(lambda: bridge._companion_preferences.worker is None and not bridge._companion_preferences.pending)
            assert library.setting('companion_panel_opacity', 100) == 30
            assert not warnings, warnings
            result = dict(status='passed', sizes=3, opacity_clicks=2, settings_preserves_binding=True,
                          subject_badge_hidden=True, qml_warnings=warnings,
                          transparency_max_ui_gap_seconds=round(max_gap, 3), transparency_broad_refreshes=len(broad_refreshes),
                          scope='Qt hit targets/geometry with intercepted commands; native Office verified separately')
            (report / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result))
        finally:
            bridge.powerpoint_worker = None
            bridge.teachingSession.clear()
            companion.setProperty('disposing', True)
            companion.hide()
            root.hide()
            for worker in (bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog, bridge.browserAI,
                           bridge.english_reader, bridge.narration_preparation, bridge.classroom, bridge.voice_controls,
                           bridge._companion_preferences):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
