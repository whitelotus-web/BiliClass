"""Disposable native input acceptance harness; no models or teacher data.

Use --interactive to exercise real keyboard/mouse events through Computer Use.
The report contains only this synthetic deck and its native playback events.
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
import wave
from multiprocessing import freeze_support
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from qt_result_preview_mascot_smoke import click, control, pump, until
from test_teaching_session import prepared_lesson

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interactive', action='store_true')
    parser.add_argument('--animated', action='store_true')
    options = parser.parse_args()
    app = QGuiApplication([])
    app.setApplicationName('BiliClass shortcut acceptance')
    QQuickStyle.setStyle('Basic')
    out = Path('reports/rc90/shortcuts')
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-keys-', ignore_cleanup_errors=True) as folder:
        lesson, preview, directory, _ = prepared_lesson(Path(folder))
        # Long, silent PCM lets pause/resume position be inspected without sound.
        for path in (directory / 'audio').glob('*.wav'):
            with wave.open(str(path), 'wb') as audio:
                audio.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                audio.writeframes(b'\0\0' * 24000 * 60)
        os.environ['BILICLASS_DATA'] = str(directory)
        library = Library(directory)
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings, events = [], []
        engine.warnings.connect(lambda values: warnings.extend(str(value) for value in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(RESOURCE_ROOT / 'qml/Main.qml')
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        try:
            window.setProperty('page', 'settings')
            settings = control(window, 'settingsPage')
            settings.setProperty('activeTab', 3)
            pump(100)
            panel = control(window, 'mascotShortcutPanel')
            button = control(window, 'shortcutBinden')
            click(window, button)
            QTest.keyClick(window, Qt.Key_A)
            pump()
            assert 'A' in control(window, 'shortcutBinden').property('text')
            click(window, control(window, 'saveMascotShortcuts'))
            assert bridge.mascotShortcuts.state['bindings']['en'] == 'A'
            assert library.setting('mascot_shortcuts', {})['en'] == 'A'
            click(window, button)
            QTest.keyClick(window, Qt.Key_F1)
            click(window, control(window, 'saveMascotShortcuts'))
            assert bridge.mascotShortcuts.state['bindings']['en'] == 'F1', 'Capture must override Main F1 Help shortcut'
            click(window, control(window, 'shortcutBindvi'))
            QTest.keyClick(window, Qt.Key_F1)
            click(window, control(window, 'saveMascotShortcuts'))
            assert bridge.mascotShortcuts.state['error'] and bridge.mascotShortcuts.state['bindings']['vi'] == 'Enter'
            click(window, control(window, 'resetMascotShortcuts'))
            click(window, control(window, 'shortcutBindboth'))
            QTest.keyClick(window, Qt.Key_K, Qt.ControlModifier)
            click(window, control(window, 'saveMascotShortcuts'))
            assert bridge.mascotShortcuts.state['bindings']['both'] == 'Ctrl+K'
            click(window, control(window, 'resetMascotShortcuts'))
            assert bridge.mascotShortcuts.state['bindings']['en'] == 'Space'
            for direction, key in [('Left', Qt.Key_A), ('Right', Qt.Key_D), ('Up', Qt.Key_W), ('Down', Qt.Key_S)]:
                click(window, control(window, 'shortcutGuide' + direction))
                pump(80)
                assert panel.property('capturing'), direction
                QTest.keyClick(window, key)
                pump()
                assert not panel.property('capturing'), direction
            click(window, control(window, 'saveMascotShortcuts'))
            chosen = bridge.mascotShortcuts.state['bindings']
            assert [chosen[k] for k in ('previous', 'next', 'volume_up', 'volume_down')] == ['A', 'D', 'W', 'S'], chosen
            assert library.setting('mascot_shortcuts', {}) == chosen
            tooltip = control(window, 'companionShortcutTooltip')
            tooltip.setProperty('visible', True)
            pump(100)
            pending = [tooltip.property('contentItem')]
            guide_keys = {}
            while pending:
                item = pending.pop()
                if item.objectName().startswith('shortcutHelpKey'):
                    guide_keys[item.objectName()] = item.property('text')
                pending.extend(item.childItems())
            assert guide_keys['shortcutHelpKey3'] == 'A / D'
            assert guide_keys['shortcutHelpKey4'] == 'W / S'
            assert guide_keys['shortcutHelpKey0'] == 'Space ␣'
            tooltip.setProperty('visible', False)
            click(window, control(window, 'resetMascotShortcuts'))
            assert not panel.property('dirty')
            for width, height in ((1920, 1080), (1366, 850), (1080, 700)):
                window.resize(width, height)
                pump(150)
                click(window, control(window, 'resetMascotShortcuts'))
                bindings = control(window, 'shortcutBindings')
                guide = control(window, 'shortcutNavigationGuide')
                bp = bindings.mapToItem(panel, QPointF())
                gp = guide.mapToItem(panel, QPointF())
                if panel.property('wideGuide'):
                    assert gp.x() >= bp.x() + bindings.width() + 20
                else:
                    assert gp.y() >= bp.y() + bindings.height() + 12
                for direction in ('Up', 'Down', 'Left', 'Right'):
                    key = control(window, 'shortcutGuide' + direction)
                    assert key.width() >= 50 and key.height() >= 48
                    point = key.mapToItem(panel, QPointF())
                    assert 0 <= point.x() <= panel.width() - key.width()
                assert window.grabWindow().save(str(out / f'keyboard-guide-{width}.png'))
            assert window.grabWindow().save(str(out / 'mascot-settings.png'))
            if options.interactive:
                if options.animated:
                    activate = bridge._activate_teaching
                    def activate_fixture(prepared):
                        import win32com.client

                        # This temporary, synthetic copy is the only deck edited.
                        office = win32com.client.DispatchEx('PowerPoint.Application')
                        deck = office.Presentations.Open(prepared['path'], ReadOnly=False, Untitled=False, WithWindow=False)
                        try:
                            slide = deck.Slides(1)
                            box = slide.Shapes.AddTextbox(1, 50, 50, 240, 50)
                            box.TextFrame.TextRange.Text = 'One click reveals this fixture.'
                            slide.TimeLine.MainSequence.AddEffect(box, 1, 0, 1)
                            deck.SlideShowSettings.ShowPresenterView = True
                            deck.Save()
                        finally:
                            deck.Close()
                        prepared['sha256'] = hashlib.sha256(Path(prepared['path']).read_bytes()).hexdigest()
                        activate(prepared)
                    bridge._activate_teaching = activate_fixture
                bridge._show_lesson(lesson, preview, destination='voice', auto_repair=False)
                until(lambda: not bridge.busy and not bridge.previewBusy)
                bridge.openNarratedPowerPoint(bridge.selectedNarrationVariant)
                until(lambda: bridge.powerpointState.get('opened'), timeout=50)
                bridge.powerpoint_worker.stateChanged.connect(lambda state: events.append(dict(state)))
                bridge.powerpoint_worker.navigate('start')
                until(lambda: bridge.powerpointState.get('active'), timeout=30)
                command_path = out / 'command.json'
                command_path.unlink(missing_ok=True)
                deadline = time.monotonic() + 900
                while time.monotonic() < deadline:
                    pump(50)
                    if command_path.is_file():
                        command = json.loads(command_path.read_text(encoding='utf-8-sig'))
                        command_path.unlink()
                        if command.get('action') == 'finish':
                            break
                        if command.get('action') == 'configure':
                            bridge.mascotShortcuts.save(command['bindings'])
                        elif command.get('action') == 'navigate':
                            bridge.powerpoint_worker.navigate(command['command'], command.get('target'))
                        elif command.get('action') == 'guide':
                            companion = control(window, 'companionWindow')
                            companion.setProperty('collapsed', False)
                            control(window, 'companionShortcutTooltip').setProperty('visible', True)
                            pump(100)
                            assert companion.grabWindow().save(str(out / 'mascot-key-guide.png'))
                    state = {'powerpoint': bridge.powerpointState, 'reader': bridge.teachingSession.reader,
                             'audio': bridge.teachingSession.audio, 'events': events, 'message': bridge.message,
                             'warnings': warnings}
                    temp = out / 'state.tmp'
                    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
                    try:
                        temp.replace(out / 'state.json')
                    except PermissionError:
                        pass  # A report reader may briefly hold this Windows file.
            assert not warnings, warnings
            (out / 'result.json').write_text(json.dumps({'settings': 'passed', 'warnings': warnings,
                                                      'interactive': options.interactive}), encoding='utf-8')
        finally:
            if bridge.powerpoint_worker:
                worker = bridge.powerpoint_worker
                bridge.stopPowerPoint()
                worker.wait(10000)
                pump(100)
            for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                           bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                           bridge.voice_controls):
                worker.shutdown()
            bridge.classroom.shutdown()
            for root in engine.rootObjects():
                root.close()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            library.close()
    print('Shortcut Qt smoke passed:', out)


if __name__ == '__main__':
    freeze_support()
    main()
