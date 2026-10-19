"""Disposable Qt geometry, settings navigation and hit testing; no Office/model."""

import json
import sqlite3
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPoint, QPointF, Qt, QTimer, QUrl, Slot
from PySide6.QtGui import QGuiApplication, QWheelEvent
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

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
    report = Path('reports/rc83/companion-controls')
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
                until(lambda: not bridge.mascotSaving)
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
            until(lambda: not bridge.mascotSaving)
            bridge._powerpoint_state = {'active': True, 'opened': True, 'slide': 2, 'total': 7, 'message': ''}
            native_commands = []
            bridge.powerpoint_worker = SimpleNamespace(navigate=lambda *args: native_commands.append(args))
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
                assert bridge.commands[-5:] == [('navigate', 'previous_slide'), ('navigate', 'next_slide'), ('read', 'en'), ('read', 'vi'), ('read', 'both')], (bridge.commands, c('companionPanelMoveArea').property('overControl'))
                # Real mouse input on the panel moves the complete window,
                # persists the mascot anchor, and never activates a control.
                area = app.primaryScreen().availableGeometry()
                bridge.saveMascotLocation(area.left() + area.width() * 2 // 3,
                                          area.top() + area.height() * 2 // 3)
                bridge.showCompanion(companion)
                pump(120)
                panel = c('companionPanelMoveArea')
                grab = panel.mapToScene(QPointF(28, 26)).toPoint()
                origin = QPoint(companion.x(), companion.y())
                commands = list(bridge.commands)
                QTest.mousePress(companion, Qt.LeftButton, pos=grab)
                QTest.mouseMove(companion, grab + QPoint(-55, -35))
                QTest.mouseRelease(companion, Qt.LeftButton, pos=grab + QPoint(-55, -35))
                pump(150)
                assert companion.x() < origin.x() - 30 and companion.y() < origin.y() - 20
                assert not companion.property('collapsed') and bridge.commands == commands
                mascot = c('mascotToggle')
                anchor = {'x': companion.x() + mascot.x(), 'y': companion.y() + mascot.y()}
                assert bridge._mascot_location == anchor
                # A regular panel click stays expanded; a double click folds
                # it into the mascot without changing the dragged anchor.
                grab = panel.mapToScene(QPointF(28, 26)).toPoint()
                QTest.mouseClick(companion, Qt.LeftButton, pos=grab)
                pump(100)
                assert not companion.property('collapsed')
                QTest.mouseDClick(companion, Qt.LeftButton, pos=grab)
                pump(150)
                assert companion.property('collapsed') and not c('companionMenu').isVisible()
                assert abs(companion.x() - anchor['x']) <= 1 and abs(companion.y() - anchor['y']) <= 1
                click(companion, mascot)
                pump(120)
                assert not companion.property('collapsed')
                # Buttons, including a double click, retain their action.
                previous = c('companionPrevious')
                center = previous.mapToScene(QPointF(previous.width() / 2, previous.height() / 2)).toPoint()
                QTest.mouseDClick(companion, Qt.LeftButton, pos=center)
                pump(100)
                assert not companion.property('collapsed')
                assert companion.grabWindow().save(str(report / f'active-opacity-{opacity}.png'))
            # Dragging a disabled control, the volume slider, or selectable
            # response text must not move the window beneath the pointer.
            origin = QPoint(companion.x(), companion.y())
            previous.setEnabled(False)
            center = previous.mapToScene(QPointF(previous.width() / 2, previous.height() / 2)).toPoint()
            QTest.mousePress(companion, Qt.LeftButton, pos=center)
            QTest.mouseMove(companion, center + QPoint(25, 0))
            QTest.mouseRelease(companion, Qt.LeftButton, pos=center + QPoint(25, 0))
            assert QPoint(companion.x(), companion.y()) == origin
            previous.setEnabled(True)
            volume = c('companionVolume')
            center = volume.mapToScene(QPointF(volume.width() * .8, volume.height() / 2)).toPoint()
            QTest.mousePress(companion, Qt.LeftButton, pos=center)
            QTest.mouseMove(companion, center - QPoint(45, 0))
            QTest.mouseRelease(companion, Qt.LeftButton, pos=center - QPoint(45, 0))
            assert QPoint(companion.x(), companion.y()) == origin
            assert native_commands and native_commands[-1][0] == 'set_volume'
            help_button = c('companionShortcutGuideToggle')
            height_without_guide = companion.height()
            QTest.mouseMove(companion, help_button.mapToScene(QPointF(15, 15)).toPoint())
            pump(300)
            until(lambda: c('companionShortcutTooltip').property('visible'))
            assert companion.height() == height_without_guide, 'Hover help must not resize the panel'
            assert companion.grabWindow().save(str(report / 'shortcut-tooltip.png'))
            QTest.mouseMove(companion, QPoint(10, 10))
            until(lambda: not c('companionShortcutTooltip').property('visible'))
            assert bridge.mascotShortcuts.state['labels']['en'] == 'Space ␣'
            assert bridge.mascotShortcuts.state['labels']['vi'] == 'Enter ↵'
            assert bridge.mascotShortcuts.state['labels']['both'] == 'Ctrl + Space ␣'
            bridge.teachingSession.response = {'untouched': False, 'text': '\n'.join(['Selectable response text.'] * 30)}
            bridge.teachingSession.changed.emit()
            pump(150)
            text = c('companionResponseText')
            click(companion, c('companionResponseScroll'))  # Scroll its viewport into view first.
            origin = QPoint(companion.x(), companion.y())
            center = text.mapToScene(QPointF(12, 15)).toPoint()
            QTest.mousePress(companion, Qt.LeftButton, pos=center)
            QTest.mouseMove(companion, center + QPoint(60, 0))
            QTest.mouseRelease(companion, Qt.LeftButton, pos=center + QPoint(60, 0))
            assert QPoint(companion.x(), companion.y()) == origin
            viewport = c('companionControlsScroll').property('contentItem')
            original_height = companion.height()
            companion.setHeight(430)
            pump(150)
            viewport.setProperty('contentY', 0)
            center = c('companionPanelMoveArea').mapToScene(QPointF(35, 65))
            event = QWheelEvent(center, QPointF(companion.mapToGlobal(center.toPoint())), QPoint(), QPoint(0, -120),
                                Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
            QGuiApplication.sendEvent(companion, event)
            pump(150)
            assert viewport.property('contentY') > 0, 'Panel movement must not swallow wheel scrolling'
            companion.setHeight(original_height)
            bridge.teachingSession.response = {'untouched': True}
            bridge.teachingSession.changed.emit()
            viewport.setProperty('contentY', 0)
            pump(100)
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
            for removed in ('mascotVisible', 'mascotExplanation', 'mascotQuiz'):
                assert c('settingsPage').findChild(QObject, removed) is None
            assert not c('mascotPreview').property('showSubjectBadge')
            assert not c('mascotPreview').findChild(QObject, 'mascotSubjectBadge').isVisible()
            for width, height in ((1366, 850), (1080, 700)):
                root.resize(width, height)
                pump(100)
                summary, toggles = c('mascotAccessorySummary'), c('mascotAlwaysOnTop')
                summary_left = summary.mapToScene(QPointF()).x()
                toggles_right = toggles.mapToScene(QPointF(toggles.width(), 0)).x()
                if c('settingsPage').width() >= 800:
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
                bridge.saveMascotPreferences('Milo', True, 110, 'right', False, True, True, True)
                pump(150)
                assert bridge.mascotSaving and not c('saveMascot').isEnabled(), 'Mascot settings save must wait off the GUI thread'
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
            assert not bridge.mascotSaving and library.setting('mascot', '') == 'Milo'
            assert not warnings, warnings
            result = dict(status='passed', sizes=3, opacity_clicks=2, settings_preserves_binding=True,
                          subject_badge_hidden=True, qml_warnings=warnings,
                          panel_drag_and_double_click=True,
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
