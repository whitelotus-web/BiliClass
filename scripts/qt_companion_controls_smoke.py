"""Disposable Qt geometry, settings navigation and hit testing; no Office/model."""

import argparse
import json
import sqlite3
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPoint, QPointF, Qt, QTimer, QUrl, Slot
from PySide6.QtGui import QGuiApplication, QWheelEvent
from PySide6.QtQml import QQmlApplicationEngine, QQmlEngine, QQmlExpression
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-dir', type=Path, default=Path('reports/companion-controls'))
    parser.add_argument('--layout-only', action='store_true')
    args = parser.parse_args()
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = args.report_dir
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-controls-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        lesson = library.create('Bài đang gắn để thử điều khiển', 'Vật lý', 'THPT', '11', [('Slide 1', 'Năng lượng.')])
        bridge = ControlBridge(library)
        # Geometry/input tests must never adjust the teacher's Windows volume.
        endpoint = [58, False]
        def system_volume(target=None):
            if target is not None:
                endpoint[:] = target, False
            return tuple(endpoint)
        bridge.teachingSession.system_volume.backend = system_volume
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
            assert not c('companionCloseLesson').isVisible()
            assert not c('mascotCompanion').findChild(QObject, 'mascotSubjectBadge').isVisible()
            assert c('companionSettings').isVisible() and c('companionShortcutGuideToggle').width() == 30
            assert companion.opacity() == 1 and bridge.companionPanelOpacity == 100
            assert companion.grabWindow().save(str(report / 'unbound.png'))
            for size, pixels, width in [('small', 80, 320), ('standard', 110, 356), ('large', 150, 400)]:
                bridge.saveMascotPreferences('Milo', True, pixels, 'right', False, True, True, True)
                until(lambda: not bridge.mascotSaving)
                pump(100)
                assert companion.width() == min(width, app.primaryScreen().availableGeometry().width() - 16)
                menu = c('companionMenu')
                button = c('companionChooseLesson')
                point = button.mapToItem(menu, QPointF())
                assert abs(point.x() - (menu.width() - point.x() - button.width())) < 1
                assert button.height() == {'small': 34, 'standard': 38, 'large': 44}[size]
                gear = c('companionSettings')
                point = gear.mapToItem(menu, QPointF())
                assert point.x() > 0 and point.x() + gear.width() < menu.width()
                assert companion.grabWindow().save(str(report / (size + '.png')))
            bridge.saveMascotPreferences('Milo', True, 110, 'right', False, True, True, True)
            until(lambda: not bridge.mascotSaving)
            bridge._powerpoint_state = {'active': True, 'opened': True, 'slide': 2, 'total': 7, 'message': ''}
            native_commands = []
            lesson['narration'] = {'keys': {}}
            bridge.powerpoint_worker = SimpleNamespace(navigate=lambda *args: native_commands.append(args), stop=lambda: native_commands.append(('stop',)))
            bridge.teachingSession.bind({'lesson': lesson, 'path': '', 'preview': {}, 'media': {2: ['en', 'vi']}})
            bridge.changed.emit()
            pump(150)
            audio = [c('companionRead' + language) for language in ('English', 'Vietnamese')]
            assert all(item.isVisible() for item in audio)
            assert max(item.width() for item in audio) - min(item.width() for item in audio) <= 1, [item.width() for item in audio]
            assert max(item.mapToScene(QPointF()).y() for item in audio) - min(item.mapToScene(QPointF()).y() for item in audio) < 1
            # Every availability transition retains two readable buttons and
            # identical geometry, including an empty slide and all panel sizes.
            for pixels in (80, 110, 150):
                bridge.saveMascotPreferences('Milo', True, pixels, 'right', False, True, True, True)
                until(lambda: not bridge.mascotSaving)
                pump(100)
                assert bridge.teachingSession.reading_scope == 'full_slide'
                before = [(item.x(), item.y(), item.width(), item.height()) for item in audio]
                height = companion.height()
                for languages in (['en'], [], ['vi'], ['en', 'vi']):
                    bridge.teachingSession.bound['media'][2] = languages
                    bridge.teachingSession.changed.emit()
                    pump(60)
                    assert all(item.isVisible() for item in audio)
                    assert [item.isEnabled() for item in audio] == [lang in languages for lang in ('en', 'vi')]
                    assert before == [(item.x(), item.y(), item.width(), item.height()) for item in audio]
                    assert c('companionAudioHint').isVisible() == (not languages)
                    assert bool(c('companionAudioHint').property('text')) == (not languages)
                    if languages:
                        assert companion.height() == height
                    else:
                        assert height < companion.height() <= height + 40, 'Only the missing-audio hint may add height'
                    assert all(item.property('iconName') == 'speaker' for item in audio)
                for suffix in ('Auto', 'Visible', 'Full', 'Options'):
                    assert root.findChild(QObject, 'companionReading' + suffix) is None
                assert companion.grabWindow().save(str(report / f'stable-speakers-{pixels}.png'))
                assert c('companionReadEnglish').mapToScene(QPointF()).y() > c('companionVolume').mapToScene(QPointF()).y()
                assert c('companionPrevious').mapToScene(QPointF()).y() > c('companionReadEnglish').mapToScene(QPointF()).y()
                geometry = (companion.x(), companion.y(), companion.height(),
                            audio[0].mapToGlobal(QPointF()).y(), audio[0].width(), audio[0].height())
                for state in ('preparing', 'reading', 'paused', 'reading', 'stopped'):
                    bridge.teachingSession.language = 'en'
                    bridge.teachingSession.native_state = state
                    bridge.teachingSession.changed.emit()
                    pump(80)
                    assert geometry == (companion.x(), companion.y(), companion.height(),
                                        audio[0].mapToGlobal(QPointF()).y(), audio[0].width(), audio[0].height()), (pixels, state, geometry, companion.x(), companion.y(), companion.height(), audio[0].mapToGlobal(QPointF()).y(), audio[0].width(), audio[0].height())
            if args.layout_only:
                assert bridge.teachingSession.reading_scope == 'full_slide'
                pump(100)
                for name in ('companionPrevious', 'companionNext', 'companionReadEnglish', 'companionReadVietnamese'):
                    click(companion, c(name))
                assert bridge.commands[-4:] == [('navigate', 'previous'), ('navigate', 'next'), ('read', 'en'), ('read', 'vi')]
                assert not warnings, warnings
                result = {'status': 'passed', 'qml_warnings': warnings, 'panel_sizes': ['small', 'standard', 'large'],
                          'audio_below_volume': True, 'navigation_below_audio': True,
                          'stable_geometry_during_play_pause': True, 'buttons_clickable': True}
                (report / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                print(json.dumps(result), flush=True)
                return
            bridge.saveMascotPreferences('Milo', True, 110, 'right', False, True, True, True)
            until(lambda: not bridge.mascotSaving)
            assert c('companionEndShow').property('danger')
            assert c('companionStartShow').property('iconName') == 'presentation'
            assert bridge.teachingSession.reading_scope == 'full_slide'
            assert root.findChild(QObject, 'companionReadingOptions') is None
            assert root.findChild(QObject, 'companionReadingMenu') is None
            assert root.findChild(QObject, 'companionReadingScope') is None
            for opacity in (100, 30):
                bridge.setCompanionPanelOpacity(opacity)
                pump(100)
                assert abs(c('companionMenu').property('color').alphaF() - opacity / 100) < .01
                assert companion.opacity() == 1 and all(item.opacity() == 1 for item in audio)
                for name in ('companionPrevious', 'companionNext', 'companionReadEnglish', 'companionReadVietnamese'):
                    click(companion, c(name))
                assert bridge.commands[-4:] == [('navigate', 'previous'), ('navigate', 'next'), ('read', 'en'), ('read', 'vi')], (bridge.commands, c('companionPanelMoveArea').property('overControl'))
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
                # A double click no longer collapses the panel. Only the down
                # arrow folds it, without changing the dragged anchor.
                grab = panel.mapToScene(QPointF(28, 26)).toPoint()
                QTest.mouseClick(companion, Qt.LeftButton, pos=grab)
                pump(100)
                assert not companion.property('collapsed')
                QTest.mouseDClick(companion, Qt.LeftButton, pos=grab)
                pump(150)
                assert not companion.property('collapsed')
                click(companion, c('collapseCompanionPanel'))
                until(lambda: not c('companionMenu').isVisible())
                assert companion.property('collapsed') and not c('companionMenu').isVisible()
                assert abs(companion.x() + mascot.x() - anchor['x']) <= 1 and abs(companion.y() + mascot.y() - anchor['y']) <= 1
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
            until(lambda: endpoint[0] == bridge.teachingSession.volume)
            assert ('set_volume', 100) in native_commands, native_commands
            assert all(command[1] == 100 for command in native_commands if command[0] == 'set_volume')
            volume = c('companionVolume')
            center = volume.mapToScene(QPointF(volume.width() / 2, volume.height() / 2))
            initial = bridge.teachingSession.volume
            scroll = c('companionControlsScroll').property('contentItem')
            scroll_position = scroll.property('contentY')
            for delta, expected in [(120, initial + 5), (-120, initial)]:
                event = QWheelEvent(center, QPointF(companion.mapToGlobal(center.toPoint())), QPoint(), QPoint(0, delta), Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
                QGuiApplication.sendEvent(companion, event)
                until(lambda: bridge.teachingSession.volume == expected)
                until(lambda: endpoint[0] == expected)
                assert endpoint[0] == expected
                assert scroll.property('contentY') == scroll_position
            def wheel_at(target, delta=0, pixels=0):
                center = target.mapToScene(QPointF(target.width()/2, target.height()/2))
                event = QWheelEvent(center, QPointF(companion.mapToGlobal(center.toPoint())),
                    QPoint(0, pixels), QPoint(0, delta), Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
                QGuiApplication.sendEvent(companion, event)
                pump(80)

            commands = list(bridge.commands)
            for name in ('companionVolumeLabel', 'companionVolumePercent', 'companionVolumeArea'):
                wheel_at(c(name), 120)
                until(lambda: bridge.teachingSession.volume == initial + 5)
                wheel_at(c(name), -120)
                until(lambda: bridge.teachingSession.volume == initial)
                assert bridge.commands == commands, (name, bridge.commands)
            wheel_at(volume, 60)
            assert bridge.teachingSession.volume == initial
            wheel_at(volume, 60)
            until(lambda: bridge.teachingSession.volume == initial + 5)
            wheel_at(volume, -120)
            until(lambda: bridge.teachingSession.volume == initial)
            for name in ('companionBoundLesson', 'companionNext', 'companionSlidePosition'):
                wheel_at(c(name), -120)
                assert bridge.commands == commands + [('navigate', 'next')], (name, bridge.commands)
                wheel_at(c(name), 120)
                commands += [('navigate', 'next'), ('navigate', 'previous')]
                assert bridge.commands == commands, (name, bridge.commands)
                assert bridge.teachingSession.volume == initial
                assert scroll.property('contentY') == scroll_position
            wheel_at(c('companionBoundLesson'), -60)
            assert bridge.commands == commands
            wheel_at(c('companionBoundLesson'), -60)
            commands += [('navigate', 'next')]
            assert bridge.commands == commands
            wheel_at(c('companionBoundLesson'), pixels=40)
            commands += [('navigate', 'previous')]
            assert bridge.commands == commands
            # An external Windows slider/hardware-key update is reflected back.
            endpoint[0] = 37
            until(lambda: bridge.teachingSession.volume == 37)
            assert round(volume.property('value')) == 37
            for name in ('companionPrevious', 'companionNext'):
                target = c(name)
                QTest.mouseMove(companion, target.mapToScene(QPointF(target.width()/2, target.height()/2)).toPoint())
                pump(650)
                hint = QQmlExpression(QQmlEngine.contextForObject(target), target, 'ToolTip.visible')
                assert hint.evaluate() == (False, False) and not hint.hasError()
            help_button = c('companionShortcutGuideToggle')
            screen_area = app.primaryScreen().availableGeometry()
            companion.setPosition(screen_area.right()-companion.width()-12, screen_area.bottom()-companion.height()-12)
            pump(100)
            QTest.mouseMove(companion, QPoint(12, 12))
            pump(100)
            height_without_guide = companion.height()
            QTest.mouseMove(companion, help_button.mapToScene(QPointF(15, 15)).toPoint())
            pump(300)
            until(lambda: c('companionShortcutTooltip').property('opened'))
            pump(100)
            tooltip = c('companionShortcutTooltip')
            geometry_expression = QQmlExpression(QQmlEngine.contextForObject(tooltip), tooltip,
                'JSON.stringify({native: contentItem.Window.window !== parent.Window.window, visible: contentItem.Window.window.visible, x: contentItem.Window.window.x, y: contentItem.Window.window.y, width: contentItem.Window.window.width, height: contentItem.Window.window.height})')
            geometry, error = geometry_expression.evaluate()
            assert not error
            native_tip = json.loads(geometry)
            assert native_tip['native'] and native_tip['visible']
            panel_top = c('companionMenu').mapToGlobal(QPointF()).y()
            panel_left = c('companionMenu').mapToGlobal(QPointF()).x()
            if panel_top-screen_area.top() >= native_tip['height']+16:
                assert native_tip['y']+native_tip['height'] <= panel_top-4, (native_tip, panel_top)
                assert abs(native_tip['x']-panel_left) <= 1, (native_tip, panel_left)
            else:
                assert (native_tip['x']+native_tip['width'] <= panel_left-4
                        or native_tip['x'] >= panel_left+c('companionMenu').width()+4), (native_tip, panel_top)
            assert companion.height() == height_without_guide, 'Hover help must not resize the panel'
            assert abs(native_tip['width']-c('companionMenu').width()) <= 1, native_tip
            tooltip_window, error = QQmlExpression(QQmlEngine.contextForObject(tooltip), tooltip, 'contentItem.Window.window').evaluate()
            assert c('shortcutGuideTitle').property('text') == 'Hướng dẫn phím và chuột'
            assert c('shortcutMouseWheelIcon').isVisible()
            for name in ('shortcutMouseNavigation', 'shortcutMouseVolume'):
                label = c(name)
                assert label.isVisible() and label.property('contentWidth') <= label.width()+1
                assert label.property('contentHeight') <= label.height()+1
            assert native_tip['y'] >= screen_area.top() and native_tip['y']+native_tip['height'] <= screen_area.bottom()+1
            assert not error and tooltip_window.grabWindow().save(str(report / 'shortcut-tooltip-window.png'))
            assert companion.grabWindow().save(str(report / 'shortcut-tooltip.png'))
            QTest.mouseMove(companion, QPoint(10, 10))
            until(lambda: not c('companionShortcutTooltip').property('visible'))
            bottom_position = companion.position()
            companion.setPosition(screen_area.left()+12, screen_area.top()+12)
            companion.raise_()
            pump(150)
            QTest.mouseMove(companion, QPoint(10, 10))
            pump(80)
            QTest.mouseMove(companion, help_button.mapToScene(QPointF(15, 15)).toPoint())
            until(lambda: tooltip.property('opened'), timeout=5)
            pump(100)
            geometry, error = geometry_expression.evaluate()
            assert not error
            edge_tip = json.loads(geometry)
            panel_left = c('companionMenu').mapToGlobal(QPointF()).x()
            assert edge_tip['x'] >= panel_left+c('companionMenu').width()+4, edge_tip
            QTest.mouseMove(companion, QPoint(10, 10))
            until(lambda: not tooltip.property('visible'))
            companion.setPosition(bottom_position)
            assert bridge.mascotShortcuts.state['labels']['en'] == 'Space ␣'
            assert bridge.mascotShortcuts.state['labels']['vi'] == 'Enter ↵'
            assert 'both' not in bridge.mascotShortcuts.state['labels']
            bridge.teachingSession.response = {'untouched': False, 'text': '\n'.join(['Selectable response text.'] * 30)}
            bridge.teachingSession.changed.emit()
            pump(150)
            if bridge.experimentalTeaching:
                text = c('companionResponseText')
                click(companion, c('companionResponseScroll'))
                origin = QPoint(companion.x(), companion.y())
                center = text.mapToScene(QPointF(12, 15)).toPoint()
                QTest.mousePress(companion, Qt.LeftButton, pos=center)
                QTest.mouseMove(companion, center + QPoint(60, 0))
                QTest.mouseRelease(companion, Qt.LeftButton, pos=center + QPoint(60, 0))
                assert QPoint(companion.x(), companion.y()) == origin
            else:
                assert not c('companionResponseScroll').isVisible()
            viewport = c('companionControlsScroll').property('contentItem')
            companion.setProperty('choosingLesson', True)
            pump(150)
            original_height = companion.height()
            companion.setHeight(min(430, original_height - 60))
            pump(150)
            viewport.setProperty('contentY', 0)
            center = c('companionPanelMoveArea').mapToScene(QPointF(35, 65))
            event = QWheelEvent(center, QPointF(companion.mapToGlobal(center.toPoint())), QPoint(), QPoint(0, -120),
                                Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
            QGuiApplication.sendEvent(companion, event)
            pump(150)
            assert viewport.property('contentY') > 0, ('Panel movement must not swallow wheel scrolling',
                viewport.height(), viewport.property('contentHeight'), companion.height(),
                companion.property('choosingLesson'), bridge.commands, event.isAccepted())
            assert bridge.commands == commands, 'Choosing a lesson must retain normal wheel scrolling'
            companion.setProperty('choosingLesson', False)
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
                accessory, subject = c('mascotAccessories'), c('mascotAccessorySubject')
                summary_left = summary.mapToScene(QPointF()).x()
                if abs(toggles.mapToScene(QPointF()).y()-accessory.mapToScene(QPointF()).y()) < 2:
                    assert toggles.mapToScene(QPointF(toggles.width(), 0)).x() < accessory.mapToScene(QPointF()).x()
                    assert summary_left > accessory.mapToScene(QPointF(accessory.width(), 0)).x()
                else:
                    assert toggles.mapToScene(QPointF(0, toggles.height())).y() < accessory.mapToScene(QPointF()).y()
                    assert accessory.mapToScene(QPointF(0, accessory.height())).y() < summary.mapToScene(QPointF()).y()
                viewport = c('settingsContentScroll').property('contentItem')
                offset = summary.mapToItem(viewport, QPointF()).y()
                viewport.setProperty('contentY', max(0, min(viewport.property('contentHeight') - viewport.height(),
                                                           viewport.property('contentY') + offset - 120)))
                pump(100)
                assert root.grabWindow().save(str(report / f'settings-{width}.png'))
                selected_subject, subject_width = subject.property('currentText'), subject.width()
                click(root, accessory)
                assert summary.isVisible() and subject.isVisible() and not subject.isEnabled()
                assert subject.property('currentText') == selected_subject and subject.width() == subject_width
                assert root.grabWindow().save(str(report / f'settings-accessories-off-{width}.png'))
                QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, subject.mapToScene(QPointF(subject.width()/2, subject.height()/2)).toPoint())
                assert QQmlExpression(QQmlEngine.contextForObject(subject), subject, 'popup.visible').evaluate() == (False, False)
                click(root, accessory)
                assert subject.isEnabled() and subject.property('currentText') == selected_subject
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
            bridge.showCompanion(companion)
            companion.setProperty('collapsed', False)
            pump(150)
            close_lesson = c('companionCloseLesson')
            assert close_lesson.isVisible() and close_lesson.isEnabled()
            click(companion, close_lesson)
            assert native_commands[-1] == ('stop',) and bridge.powerpointState['closing']
            assert not warnings, warnings
            result = dict(status='passed', sizes=3, opacity_clicks=2, settings_preserves_binding=True,
                          subject_badge_hidden=True, fixed_two_speakers=True, availability_geometry_stable=True, plain_speaker_icons=True, qml_warnings=warnings,
                          panel_drag_and_down_arrow=True,
                          shortcut_tooltip_above_panel=True, shortcut_tooltip_edge_fallback_without_overlap=True,
                          wheel_volume_5_percent=True, wheel_volume_whole_row=True, wheel_navigation_outside_volume=True,
                          fractional_and_pixel_wheel=True, mouse_guide_visible_and_fits_screen=True,
                          system_volume_two_way=True, navigation_tooltips_removed=True,
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
