"""Real Office/Windows input, restricted to disposable windows and silent audio."""

import hashlib
import json
import os
import sys
import tempfile
import time
import wave
from multiprocessing import freeze_support
from pathlib import Path

import win32api
import win32com.client
import win32con
import win32gui
from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QPointF, Qt, QTimer, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.teaching_session import prepare_teaching
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump, until

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_teaching_session import prepared_lesson


class InputBridge(Bridge):
    def __init__(self, library):
        super().__init__(library)
        self.navigation_started = None
        self.navigation_latencies = []

    @Slot(str)
    def navigatePowerPoint(self, command):
        if command in {'next', 'previous', 'next_slide', 'previous_slide'}:
            self.navigation_started = time.monotonic()
        super().navigatePowerPoint(command)

    @Slot(object)
    def _powerpoint_changed(self, state):
        previous = self.powerpointState.get('slide')
        super()._powerpoint_changed(state)
        if (self.navigation_started is not None and state.get('active')
                and state.get('slide') != previous):
            self.navigation_latencies.append(time.monotonic() - self.navigation_started)
            self.navigation_started = None


def native_click(window, point):
    """Never click a coordinate that is covered by another application's window."""
    left, top = win32gui.ClientToScreen(int(window.winId()), (0, 0))
    scale = window.devicePixelRatio()
    target = (left + round(point.x() * scale), top + round(point.y() * scale))
    win32api.SetCursorPos(target)
    pump(180)  # Let an old hover tooltip close before checking the hit window.
    actual = win32gui.GetAncestor(win32gui.WindowFromPoint(target), 2)
    if actual != int(window.winId()):
        window.grabWindow().save('reports/rc90/occluded-input.png')
        print('Occluded ' + str((target, win32gui.GetClassName(actual), win32gui.GetWindowRect(int(window.winId())), window.size().toTuple())), flush=True)
    assert actual == int(window.winId()), target
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    pump(35)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    pump(120)


def native_key(vk, hwnd, *, ctrl=False):
    assert win32gui.GetForegroundWindow() == hwnd, 'Refuse input to an unrelated foreground application'
    if ctrl:
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(vk, 0, 0, 0)
    pump(50)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
    if ctrl:
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    pump(200)


def main():
    app = QGuiApplication([])
    app.setApplicationName('BiliClass companion input verification')
    QQuickStyle.setStyle('Basic')
    report = Path(os.environ.get('BILICLASS_INPUT_REPORT', 'reports/rc90/native-input'))
    report.mkdir(parents=True, exist_ok=True)
    cursor = win32api.GetCursorPos()
    with tempfile.TemporaryDirectory(prefix='bcl-input-', ignore_cleanup_errors=True) as folder:
        lesson, preview, directory, source = prepared_lesson(Path(folder))
        original = source.read_bytes()
        for path in (directory / 'audio').glob('*.wav'):
            with wave.open(str(path), 'wb') as audio:
                audio.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                audio.writeframes(b'\0\0' * 24000 * 60)
        os.environ['BILICLASS_DATA'] = str(directory)
        prepared = prepare_teaching(lesson, preview, directory)
        # An on-click effect proves mouse slide navigation is distinct from builds.
        office = win32com.client.DispatchEx('PowerPoint.Application')
        deck = office.Presentations.Open(prepared['path'], ReadOnly=False, Untitled=False, WithWindow=False)
        try:
            slide = deck.Slides(1)
            box = slide.Shapes.AddTextbox(1, 50, 50, 240, 50)
            box.TextFrame.TextRange.Text = 'Disposable animation fixture.'
            slide.TimeLine.MainSequence.AddEffect(box, 1, 0, 1)
            deck.SlideShowSettings.ShowPresenterView = False
            deck.Save()
        finally:
            deck.Close()
        prepared['sha256'] = hashlib.sha256(Path(prepared['path']).read_bytes()).hexdigest()
        library = Library(directory)
        bridge = InputBridge(library)
        endpoint = [80, False]
        def fixture_volume(target=None):
            if target is not None:
                endpoint[:] = target, False
            return tuple(endpoint)
        bridge.teachingSession.system_volume.backend = fixture_volume
        engine = QQmlApplicationEngine()
        warnings, broad_refreshes, ticks = [], [], []
        engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(RESOURCE_ROOT / 'qml/Main.qml')
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')
        other = QQuickWindow()
        other.setFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        other.setTitle('BiliClass disposable keyboard background')
        other.setGeometry(70, 70, 250, 160)
        beat = QTimer()
        beat.setInterval(10)
        beat.timeout.connect(lambda: ticks.append(time.monotonic()))

        def c(name):
            return control(root, name)

        def tap(name):
            pump(180)
            item = c(name)
            assert item.isVisible() and item.isEnabled(), name
            print('Tap ' + name + ' ' + str(item.mapToScene(QPointF()).toTuple()), flush=True)
            companion.grabWindow().save(str(report / (name + '.png')))
            native_click(companion, item.mapToScene(QPointF(item.width() / 2, item.height() / 2)).toPoint())

        def background():
            other.show()
            other.raise_()
            other.requestActivate()
            until(other.isExposed)
            win32gui.SetWindowPos(int(other.winId()), win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
            pump(250)
            for _ in range(3):
                native_click(other, QPoint(120, 70))
                if win32gui.GetForegroundWindow() == int(other.winId()):
                    break
                pump(250)  # Allow the one queued F5 activation to finish.
            assert win32gui.GetForegroundWindow() == int(other.winId())

        def mascot():
            item = c('mascotToggle')
            native_click(companion, item.mapToScene(QPointF(item.width() / 2, item.height() / 2)).toPoint())

        try:
            root.setProperty('page', 'settings')
            c('settingsPage').setProperty('activeTab', 3)
            until(lambda: bridge._catalog.worker is None)
            area = app.primaryScreen().availableGeometry()
            bridge.saveMascotLocation(area.left() + area.width() // 3, area.bottom() - 170)
            bridge.showCompanion(companion)
            background()
            mascot()
            assert win32gui.GetForegroundWindow() == int(other.winId()), 'An unbound Mascot must not steal another app'
            bridge._lesson = lesson
            bridge._activate_teaching(prepared)
            until(lambda: bridge.powerpointState.get('opened'), timeout=50)
            editor = bridge.powerpointState.get('focus_hwnd')
            assert editor, bridge.powerpointState
            background()
            mascot()
            until(lambda: win32gui.GetForegroundWindow() == editor)
            native_key(win32con.VK_F5, editor)
            until(lambda: bridge.powerpointState.get('active'), timeout=35)
            hwnd = bridge.powerpointState['hwnd']
            until(lambda: win32gui.GetForegroundWindow() == hwnd)
            companion.setProperty('collapsed', False)
            bridge.showCompanion(companion)
            pump(150)
            assert c('companionSlidePosition').property('text') == 'Slide 1 / 3'
            assert c('companionPrevious').isEnabled()
            background()
            tap('companionReadEnglish')
            until(lambda: bridge.teachingSession.native_state == 'reading')
            assert win32gui.GetForegroundWindow() == hwnd
            # Ignore other decks (including protected windows) completely.
            owned = None
            for candidate in win32com.client.Dispatch('PowerPoint.Application').Presentations:
                try:
                    if Path(candidate.FullName).resolve() == Path(prepared['path']).resolve():
                        owned = candidate
                        break
                except Exception:
                    continue
            assert owned is not None, 'The disposable presentation must be reachable through its exact path'
            native_slide = owned.Slides(1)
            ready = next(s for s in native_slide.Shapes if s.Name == 'BiliClass control EN')
            badge = next(s for s in native_slide.Shapes if s.Name == 'BiliClass pause EN')
            from app.slideshow_controls import speaker_regions

            def click_slide_speaker():
                region = speaker_regions([('en', ready.Left, ready.Top, ready.Width, ready.Height)],
                                         hwnd, owned.PageSetup.SlideWidth, owned.PageSetup.SlideHeight)[0]
                target = (round((region[1]+region[3])/2), round((region[2]+region[4])/2))
                assert win32gui.GetAncestor(win32gui.WindowFromPoint(target), 2) == hwnd
                win32api.SetCursorPos(target)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                pump(35)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                pump(120)

            until(lambda: bool(badge.Visible) and not ready.Visible)
            background()
            pump(400)
            # PowerPoint can itself pause media on focus loss; the shared
            # state must reflect that before the first slide click toggles it.
            expected = 'reading' if bridge.teachingSession.native_state == 'paused' else 'paused'
            click_slide_speaker()
            until(lambda: bridge.teachingSession.native_state == expected)
            until(lambda: win32gui.GetForegroundWindow() == hwnd)
            if expected == 'reading':
                click_slide_speaker()
                until(lambda: bridge.teachingSession.native_state == 'paused')
            until(lambda: bool(ready.Visible) and not badge.Visible)
            tap('companionReadEnglish')
            until(lambda: bridge.teachingSession.native_state == 'reading')
            native_key(win32con.VK_SPACE, hwnd)
            until(lambda: bridge.teachingSession.native_state == 'paused')
            native_key(win32con.VK_SPACE, hwnd)
            until(lambda: bridge.teachingSession.native_state == 'reading')
            native_key(win32con.VK_RETURN, hwnd)
            until(lambda: bridge.teachingSession.language == 'vi')
            native_key(win32con.VK_SPACE, hwnd, ctrl=True)
            until(lambda: bridge.teachingSession.language == 'both')
            native_key(win32con.VK_UP, hwnd)
            until(lambda: bridge.teachingSession.volume == 85)
            native_key(win32con.VK_DOWN, hwnd)
            until(lambda: bridge.teachingSession.volume == 80)
            bridge.teachingSession.stop()
            bridge.teachingSession.setReadingScope('visible')
            tap('companionReadEnglish')
            until(lambda: bridge.englishReaderState['state'] == 'reading')
            until(lambda: bool(badge.Visible) and not ready.Visible)
            native_players = [owned.SlideShowWindow.View.Player(s.Id) for s in native_slide.Shapes
                              if s.Name.startswith('BiliClass audio ')]
            assert all(p.State != 0 for p in native_players), 'Cached reading must stop every native player first'
            background()
            click_slide_speaker()
            until(lambda: bridge.englishReaderState['state'] == 'paused')
            until(lambda: bool(ready.Visible) and not badge.Visible)
            assert all(p.State != 0 for p in native_players), 'Slide click must pause the cache, never start a second player'
            bridge.teachingSession.setReadingScope('auto')
            background()
            token = bridge.teachingSession.token
            native_key(win32con.VK_SPACE, int(other.winId()))
            assert bridge.teachingSession.token == token, 'Keys in an unrelated foreground app must pass through'
            bridge.changed.connect(lambda: broad_refreshes.append(1))
            beat.start()
            # Buttons reveal/rewind builds before changing the slide.
            tap('companionNext')
            until(lambda: bridge.powerpointState.get('click_index') == 1)
            assert bridge.powerpointState['slide'] == 1
            tap('companionPrevious')
            until(lambda: bridge.powerpointState.get('click_index') == 0)
            assert bridge.powerpointState['slide'] == 1
            tap('companionNext')
            until(lambda: bridge.powerpointState.get('click_index') == 1)
            tap('companionNext')
            until(lambda: bridge.powerpointState.get('slide') == 2)
            assert c('companionSlidePosition').property('text') == 'Slide 2 / 3'
            assert all(not c('companionRead' + language).isVisible()
                       for language in ('English', 'Vietnamese', 'Both'))
            assert c('companionAudioHint').isVisible()
            tap('companionPrevious')
            until(lambda: bridge.powerpointState.get('slide') == 1)
            if bridge.powerpointState['click_index'] > 0:
                tap('companionPrevious')
                until(lambda: bridge.powerpointState.get('click_index') == 0)
            before = bridge.powerpointState['click_index']
            native_key(win32con.VK_RIGHT, hwnd)
            until(lambda: bridge.powerpointState.get('click_index') != before)
            assert bridge.powerpointState['slide'] == 1, 'Keyboard arrows retain native animation builds'
            assert c('companionSlidePosition').property('text') == 'Slide 1 / 3'
            tap('companionNext')
            until(lambda: bridge.powerpointState.get('slide') == 2)
            tap('companionNext')
            until(lambda: bridge.powerpointState.get('slide') == 3)
            assert c('companionNext').isEnabled()
            assert c('companionReadVietnamese').isEnabled() and not c('companionReadEnglish').isEnabled()
            # Repeated actual mouse actions while Settings remains open.
            for _ in range(5):
                tap('companionPrevious')
                until(lambda: bridge.powerpointState.get('slide') == 2)
                tap('companionNext')
                until(lambda: bridge.powerpointState.get('slide') == 3)
            from app.slideshow_shortcuts import DEFAULTS

            assert bridge.mascotShortcuts.save(DEFAULTS | {'previous': 'A', 'next': 'D', 'volume_up': 'W', 'volume_down': 'S'})
            pump(250)
            bridge.focusTeachingPresentation()
            native_key(ord('A'), hwnd)
            until(lambda: bridge.powerpointState.get('slide') == 2)
            native_key(ord('D'), hwnd)
            until(lambda: bridge.powerpointState.get('slide') == 3)
            native_key(ord('W'), hwnd)
            until(lambda: bridge.teachingSession.volume == 85)
            native_key(ord('S'), hwnd)
            until(lambda: bridge.teachingSession.volume == 80)
            for dx, dy in [(-20, -12), (20, 12)] * 6:
                pump(100)
                left, top, _, _ = win32gui.GetWindowRect(int(companion.winId()))
                scale = companion.devicePixelRatio()
                start = (left + round(40 * scale), top + round(25 * scale))
                assert win32gui.GetAncestor(win32gui.WindowFromPoint(start), 2) == int(companion.winId())
                origin = (companion.x(), companion.y())
                win32api.SetCursorPos(start)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                pump(25)
                win32api.SetCursorPos((start[0] + round(dx * scale), start[1] + round(dy * scale)))
                pump(40)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                pump(120)
                assert abs(companion.x() - origin[0] - dx) <= 2
                assert abs(companion.y() - origin[1] - dy) <= 2
            assert not broad_refreshes, 'Office events must not rebuild every Settings/library binding'
            pump(300)
            max_gap = max(b - a for a, b in zip(ticks, ticks[1:]))
            assert max_gap < .5, max_gap
            assert companion.grabWindow().save(str(report / 'slide-three.png'))
            assert not warnings, warnings
            assert source.read_bytes() == original
            delays = bridge.navigation_latencies
            assert len(delays) == 16 and max(delays) < 1, delays  # Includes two live A/D actions.
            result = dict(status='passed', native_mouse_and_keyboard=True, f5_from_editor=True,
                          mascot_restores_foreground=True, read_pause_resume_switch=True,
                          no_capture_in_other_apps=True, mouse_and_keyboard_preserve_effects=True,
                          cached_and_native_speakers_share_pause_badges=True, wasd_live_reassignment=True,
                          voice_buttons_match_slide=True, broad_refreshes=len(broad_refreshes),
                          native_panel_drags=12, navigation_count=len(delays),
                          navigation_max_seconds=round(max(delays), 3),
                          navigation_mean_seconds=round(sum(delays) / len(delays), 3),
                          max_ui_tick_gap_seconds=round(max_gap, 3), warnings=warnings)
            (report / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            beat.stop()
            other.close()
            if bridge.powerpoint_worker:
                worker = bridge.powerpoint_worker
                bridge.stopPowerPoint()
                worker.wait(10000)
                pump(100)
            for task in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                         bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                         bridge.voice_controls, bridge._companion_preferences):
                task.shutdown()
            bridge.classroom.shutdown()
            companion.setProperty('disposing', True)
            companion.hide()
            root.close()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            library.close()
            win32api.SetCursorPos(cursor)


if __name__ == '__main__':
    freeze_support()
    main()
