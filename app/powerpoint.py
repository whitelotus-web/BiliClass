"""Read-only PowerPoint control isolated from the desktop UI process."""

import hashlib
import multiprocessing
import queue
import re
import threading
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal


def slide_for_locator(locator):
    match = re.match(r"^Slide\s+(\d+)(?:\D|$)", locator)
    return int(match.group(1)) if match else None


def slide_segment_indexes(lesson, slide, source_map=(), segment_map=()):
    """Resolve the displayed slide, including blank slides and split source text."""
    if type(slide) is not int or slide < 1:
        return []
    segments = lesson.get("segments", [])
    if segment_map:
        segment_id = segment_map[slide - 1] if slide <= len(segment_map) else None
        return [i for i, segment in enumerate(segments) if segment["id"] == segment_id]
    if source_map:
        if slide > len(source_map):
            return []
        slide = source_map[slide - 1]
    return [i for i, segment in enumerate(segments)
            if slide_for_locator(segment.get("locator", "")) == slide]


def verified_presentation(lesson, library_directory):
    source = lesson.get("source") or {}
    filename = source.get("file", "")
    if not filename or Path(filename).suffix.lower() != ".pptx":
        raise ValueError("Bài này không có tệp PowerPoint gốc. Dùng Xem trước văn bản.")
    if Path(filename).name != filename or ":" in filename:
        raise ValueError("Đường dẫn tệp nguồn không hợp lệ.")
    path = Path(library_directory) / "sources" / filename
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
        raise ValueError("Bản PowerPoint nguồn đã thay đổi hoặc bị thiếu. Hãy nhập lại tài liệu.")
    return path


def _deck_window_title(title, path):
    # A stem substring can bind Lesson.pptx to Lesson extra.pptx instead.
    return bool(re.search(r'(?:^|\[)' + re.escape(Path(path).name) + r'(?=$|\s|\])', title, re.IGNORECASE))


def slideshow_handle(path):
    """Resolve the native window without relying on optional COM HWND members."""
    import win32gui

    matches = []

    def collect(hwnd, _):
        if (win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == "screenClass"
                and _deck_window_title(win32gui.GetWindowText(hwnd), path)):
            matches.append(hwnd)

    win32gui.EnumWindows(collect, None)
    return matches[-1] if len(matches) == 1 else 0


def presenter_handle(path):
    import win32gui

    matches = []
    def collect(hwnd, _):
        if (win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) in {'PPTPresenterView', 'PodiumParent'}
                and _deck_window_title(win32gui.GetWindowText(hwnd), path)):
            matches.append(hwnd)
    win32gui.EnumWindows(collect, None)
    return matches[0] if len(matches) == 1 else 0


def editor_handle(path):
    """Only the bound presentation's editor; Office may omit DocumentWindow.HWND."""
    import win32gui

    matches = []
    def collect(hwnd, _):
        if (win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == 'PPTFrameClass'
                and _deck_window_title(win32gui.GetWindowText(hwnd), path)):
            matches.append(hwnd)
    win32gui.EnumWindows(collect, None)
    return matches[0] if len(matches) == 1 else 0


def focus_presentation(path, hwnd, pid):
    """Return keyboard input to an explicitly clicked, exact bound Office window.

    A recycled HWND or another deck in the same PowerPoint process is not a
    valid target. No COM call or foreground-input attachment runs on the GUI.
    """
    import win32con
    import win32gui
    import win32process

    if type(hwnd) is not int or not hwnd or type(pid) is not int or not pid:
        return False
    try:
        if (not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd)
                or win32process.GetWindowThreadProcessId(hwnd)[1] != pid
                or win32gui.GetClassName(hwnd) not in {'PPTFrameClass', 'screenClass', 'PPTPresenterView', 'PodiumParent'}
                or not _deck_window_title(win32gui.GetWindowText(hwnd), path)):
            return False
        if win32gui.GetForegroundWindow() == hwnd:
            return True
        # A hung Office window must not hang Mascot as well.
        win32gui.SendMessageTimeout(hwnd, win32con.WM_NULL, 0, 0, win32con.SMTO_ABORTIFHUNG, 80)
        if win32gui.IsIconic(hwnd):
            import ctypes
            from ctypes import wintypes

            restore = ctypes.windll.user32.ShowWindowAsync
            restore.argtypes = [wintypes.HWND, ctypes.c_int]
            restore.restype = wintypes.BOOL
            restore(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return win32gui.GetForegroundWindow() == hwnd
    except Exception:
        return False


def _control_media(command, target, slide_id, players, languages, playing):
    """Apply queued input only after resolving the real Office slide/players."""
    if command not in {'stop_media', 'play_media', 'pause_media', 'resume_media'}:
        return None, playing
    request = target if isinstance(target, dict) else {}
    token = request.get('token', target if command == 'stop_media' else None)
    language = request.get('language', target if command == 'play_media' else '')
    event = {'slide_id': slide_id, 'token': token, 'language': language, 'operation': command}
    if (request and request.get('slide_id') != slide_id) or (slide_id is None and command != 'stop_media'):
        return dict(event, event='media_rejected'), playing
    try:
        if command in {'stop_media', 'play_media'}:
            for identity, player in players.items():
                try:
                    player.Stop()
                except Exception:
                    if identity in playing:
                        raise  # Never acknowledge a stop while selected media may still play.
            playing = set()
        if command == 'stop_media':
            return dict(event, event='media_stopped'), playing
        if command == 'play_media':
            identity = next((key for key, lang in languages.items() if lang == language and key in players), None)
            if identity is None:
                raise ValueError('Native player unavailable')
            players[identity].Play()
            return dict(event, event='media_started'), {identity}
        if not playing:
            raise ValueError('Native player no longer selected')
        for identity in playing:
            if command == 'pause_media':
                players[identity].Pause()
            else:
                players[identity].Play()
        return dict(event, event='media_paused' if command == 'pause_media' else 'media_resumed'), playing
    except Exception:
        return dict(event, event='media_error', message='PowerPoint chưa điều khiển được loa này. Kiểm tra thiết bị âm thanh hoặc dùng giọng đã lưu.'), playing


def _native_pause_event(playing, audible, paused, previous_paused):
    """Observe native toolbar/slide actions as well as commands from Mascot."""
    if playing.intersection(paused) and not audible and not previous_paused:
        return 'media_paused'
    if previous_paused.intersection(audible):
        return 'media_resumed'
    return ''


def previous_build(view):
    """Previous() skips builds; GotoClick rewinds a click within this slide."""
    try:
        index = int(view.GetClickIndex())
    except Exception:
        index = 0
    if index > 0:
        view.GotoClick(index - 1)
    else:
        view.Previous()


def _office_session(path, initial_slide, commands, events, autostart=True, shortcuts=None):
    import psutil
    import pythoncom
    import win32com.client
    import win32process

    from .office_retry import call as office_call
    from .office_retry import is_busy
    from .slideshow_controls import prepare_controls, speaker_regions
    from .slideshow_shortcuts import SlideshowKeys

    keys = SlideshowKeys(shortcuts)
    parent = multiprocessing.parent_process()

    existing_office = any(
        (p.info["name"] or "").lower() == "powerpnt.exe" for p in psutil.process_iter(["name"])
    )
    pythoncom.CoInitialize()
    application = presentation = window = view = slide = None
    players = {}
    player_languages = {}
    playing = set()
    previous_paused = set()
    badges = {}
    overlay = None
    cached_badge = None
    volume = 100
    boxes = []
    media_starting = 0
    media_token = None
    presenter = 0
    hwnd = 0
    handles_refreshed = 0
    slide_media = {}
    current_audio = []
    focus_after_start = False

    def stop_media():
        nonlocal playing
        for identity in playing:
            try:
                players[identity].Stop()
            except Exception:
                pass
        playing = set()

    def start_show():
        nonlocal window, view, players, playing
        window = office_call(lambda: presentation.SlideShowSettings.Run())
        view = window.View
        office_call(lambda: view.GotoSlide(initial_slide))
        players, playing = {}, set()

    def progress(message):
        events.put({"active": False, "starting": True, "slide": 0, "total": 0, "message": message})

    def controls_warning():
        events.put({'event': 'input_warning', 'message': 'Chưa đổi được biểu tượng loa. Vẫn có thể phát/tạm dừng bằng Mascot.'})

    def paint_speakers(regions, active_languages=(), slide_id=None):
        nonlocal overlay
        if overlay:
            try:
                overlay.update(hwnd, regions, active_languages)
            except Exception:
                overlay.close()
                overlay = None
                keys.bind(hwnd, slide_id, (), presenter)
                events.put({'event': 'input_warning', 'message':
                            'Chưa hiển thị được loa trên slide. Dùng nút đọc trên Mascot.'})

    try:
        progress("Đang kết nối PowerPoint…")
        application = office_call(lambda: win32com.client.DispatchEx("PowerPoint.Application"))
        progress("Đang mở bài giảng trong PowerPoint…")
        presentation = office_call(lambda: application.Presentations.Open(path, ReadOnly=True, Untitled=False, WithWindow=not autostart))
        presentation.SlideShowSettings.ShowType = 1  # ppShowTypeSpeaker: native full-screen slideshow.
        if shortcuts is not None:
            keys.start()
        if shortcuts is not None and not keys.error:
            try:
                from .slideshow_overlay import SpeakerOverlay

                overlay = SpeakerOverlay()
            except Exception:
                controls_warning()
        try:
            slide_media, badges, other_media = prepare_controls(presentation, path, add_badges=overlay is not None,
                                                                 overlay=overlay is not None,
                                                                 on_warning=controls_warning)
            if badges and not other_media:
                presentation.SlideShowSettings.ShowMediaControls = False
        except Exception:
            controls_warning()
        total = presentation.Slides.Count
        slide_width, slide_height = float(presentation.PageSetup.SlideWidth), float(presentation.PageSetup.SlideHeight)
        if keys.error:
            events.put({'event': 'input_warning', 'message': keys.error})
        initial_slide = max(1, min(initial_slide, total))
        if autostart:
            start_show()
        last = None
        build_started = time.monotonic()
        while True:
            if parent is not None and not parent.is_alive():
                break  # A crashed desktop must not leave a hook or bound deck behind.
            try:
                command, target = commands.get(timeout=0.15)
            except queue.Empty:
                command, target = None, None
            if command == "stop":
                break
            pythoncom.PumpWaitingMessages()
            if command == 'set_shortcuts':
                keys.configure(target)
            if command == 'set_volume' and type(target) is int and 0 <= target <= 100:
                try:
                    for _, _, shape in current_audio if view and target != volume else []:
                        shape.MediaFormat.Volume = target / 100
                    volume = target
                    events.put({'event': 'volume_changed', 'volume': volume})
                except Exception:
                    events.put({'event': 'input_warning', 'message': 'PowerPoint chưa áp dụng được âm lượng. Dùng thanh âm lượng Windows để kiểm tra.'})
            # Resolve only THIS presentation, never the foreground Office deck.
            if view is None:
                keys.bind()
                if overlay:
                    overlay.update()
                try:
                    window = presentation.SlideShowWindow
                    view = window.View
                except Exception:
                    if not autostart and presentation.Windows.Count == 0:
                        break  # Teacher closed the deck while it was ready.
            if command == "start" and view is None:
                start_show()
                focus_after_start = True
            if command == "end_show" and view is not None:
                stop_media()
                view.Exit()
                window = view = None
                players, playing = {}, set()
            if view is None:
                keys.bind()
                media_event, playing = _control_media(command, target, None, {}, {}, set())
                if media_event:
                    events.put(media_event)
                editor = editor_handle(path)
                state = ("ready", editor)
                if state != last:
                    events.put({"active": False, "opened": True, "starting": False,
                                "slide": initial_slide, "total": total,
                                "focus_hwnd": editor,
                                "focus_pid": win32process.GetWindowThreadProcessId(editor)[1] if editor else 0,
                                "message": "Đã gắn bài với Mascot · Bấm Trình chiếu (F5)."})
                    last = state
                continue
            if command == "goto":
                if type(target) is int and 1 <= target <= total:
                    office_call(lambda: view.GotoSlide(target))
            elif command == "next":
                office_call(view.Next)  # Office handles animation builds before advancing the slide.
            elif command == "previous":
                office_call(lambda: previous_build(view))
            elif command in {"next_slide", "previous_slide"}:
                number = view.Slide.SlideIndex + (1 if command == "next_slide" else -1)
                if 1 <= number <= total:
                    stop_media()
                    office_call(lambda: view.GotoSlide(number))
            try:
                slide = office_call(lambda: view.Slide)
                position = (slide.SlideIndex, slide.SlideID)
                if not isinstance(last, tuple) or last[:2] != position:
                    # Paint before GetClickIndex too: Office may wait for its
                    # animation/media pipeline even for this metadata request.
                    hwnd = slideshow_handle(path)
                    early_boxes = slide_media.get(position[1], ([], []))[1]
                    early_regions = speaker_regions(early_boxes, hwnd, slide_width, slide_height)
                    keys.bind(hwnd, position[1], early_regions if overlay else (), presenter)
                    paint_speakers(early_regions, slide_id=position[1])
                try:
                    click_index = int(view.GetClickIndex())
                except Exception:
                    click_index = None
                current = (*position, click_index)
            except Exception:
                if autostart:
                    break
                window = view = None
                keys.bind()
                players, playing = {}, set()
                continue  # Esc returns to the bound deck; F5 can start it again.
            if current != last:
                build_started = time.monotonic()
                slide_changed = not isinstance(last, tuple) or current[0] != last[0]
                if slide_changed:
                    cached_badge = None
                    stop_media()
                    players = {}
                    player_languages = {}
                    playing = set()
                    previous_paused = set()
                    media_token = None
                    current_audio, boxes = slide_media.get(current[1], ([], []))
                if not hwnd or focus_after_start or not isinstance(last, tuple) or last[0] == 'ready':
                    hwnd = slideshow_handle(path)
                    handles_refreshed = 0
                events.put({"active": True, "opened": True, "starting": False,
                            "slide": current[0], "slide_id": current[1], "total": total,
                            "hwnd": hwnd, "click_index": click_index, "build_started": build_started,
                            "focus_hwnd": hwnd,
                            "focus_pid": win32process.GetWindowThreadProcessId(hwnd)[1] if hwnd else 0,
                            "focus_requested": focus_after_start,
                            "message": f"PowerPoint · slide {current[0]}/{total}"})
                focus_after_start = False
                last = current
                if slide_changed:
                    for identity, language, shape in current_audio:
                        try:
                            players[identity] = office_call(lambda: view.Player(identity))
                            player_languages[identity] = language
                        except Exception:
                            pass
            media_event, playing = _control_media(command, target, current[1], players, player_languages, playing)
            if command in {'stop_media', 'play_media'}:
                cached_badge = None
            elif command == 'set_reading_badge' and isinstance(target, dict) and target.get('slide_id') == current[1]:
                cached_badge = target.get('language')
            if media_event:
                events.put(media_event)
                if media_event['event'] == 'media_started':
                    media_starting = time.monotonic() + 2
                    media_token = media_event['token']
            if time.monotonic() - handles_refreshed >= 1:
                hwnd = slideshow_handle(path)
                presenter = presenter_handle(path)
                handles_refreshed = time.monotonic()
            # Refresh screen geometry as the teacher can change monitor/DPI
            # without changing slides. Hit-testing never covers source content.
            regions = speaker_regions(boxes, hwnd, slide_width, slide_height)
            keys.bind(hwnd, current[1], regions if overlay else (), presenter)
            # Input belongs to the real slide at key-down, never the currently
            # browsed lesson or a slide changed while Office was busy.
            while not keys.actions.empty():
                language, requested_slide = keys.actions.get_nowait()
                if requested_slide == current[1]:
                    events.put({'event': 'read_requested', 'language': language, 'slide_id': requested_slide})
            now_playing = set()
            paused = set()
            for identity, player in players.items():
                try:
                    state = int(player.State)
                    if state == 0:  # ppPlaying
                        now_playing.add(identity)
                    elif state == 1:
                        paused.add(identity)
                except Exception:
                    pass
            newly_playing = now_playing - playing
            if now_playing:
                media_starting = 0
            if newly_playing:
                newest = max(newly_playing)
                for identity in (now_playing | paused) - {newest}:
                    try:
                        players[identity].Stop()
                    except Exception:
                        pass
                media_token = None  # Native click, rather than a queued Mascot request.
                events.put({"event": "media_started", "language": player_languages.get(newest, ""), 'slide_id': current[1]})
                now_playing = {newest}
            elif playing and not now_playing and command != "pause_media":
                # A paused player stays selected so Resume can address it.
                if not playing.intersection(paused) and time.monotonic() >= media_starting:
                    events.put({"event": "media_finished", 'slide_id': current[1], 'token': media_token})
            if not newly_playing:
                observed = _native_pause_event(playing, now_playing, paused, previous_paused)
                acknowledged = 'media_paused' if command == 'pause_media' else 'media_resumed' if command == 'resume_media' else ''
                if observed and observed != acknowledged:
                    events.put({'event': observed, 'slide_id': current[1], 'token': media_token})
            previous_paused = playing.intersection(paused) if not newly_playing else set()
            if command == "pause_media" or (playing and not now_playing and playing.intersection(paused)):
                now_playing = playing
            elif playing and not now_playing and time.monotonic() < media_starting:
                now_playing = playing
            playing = now_playing
            visible_badges = {(current[1], identity) for identity in now_playing - paused}
            visible_badges.update((current[1], identity) for identity, language in player_languages.items()
                                  if cached_badge and language == cached_badge)
            paint_speakers(regions, {language for identity, language in player_languages.items()
                                    if (current[1], identity) in visible_badges}, current[1])
    except Exception as exc:
        import logging

        logging.exception('PowerPoint session failed')
        message = ('PowerPoint đang bận. Đóng hộp thoại trong PowerPoint rồi bấm Mở PowerPoint để thử lại.'
                   if is_busy(exc) else 'Chưa mở hoặc điều khiển được PowerPoint. Kiểm tra PowerPoint rồi thử mở bài lại.')
        events.put({"error": message + ' Bài giảng và giọng đã lưu được giữ nguyên.'})
    finally:
        keys.close()
        if overlay:
            overlay.close()
        if window is not None:
            try:
                view.Exit()
            except Exception:
                pass
        if presentation is not None:
            try:
                # Changing in-memory slideshow settings dirties even a read-only
                # deck. Discard those settings without a Save As dialog or write.
                presentation.Saved = True
                presentation.Close()  # Only the read-only deck this session opened.
            except Exception:
                pass
        if application is not None and not existing_office:
            try:
                if application.Presentations.Count == 0:
                    application.Quit()
            except Exception:
                pass
        slide = view = window = presentation = application = None
        pythoncom.CoUninitialize()


class PowerPointSession(QThread):
    stateChanged = Signal(object)
    failed = Signal(str)

    def __init__(self, path, initial_slide=1, parent=None, *, autostart=True, shortcuts=None):
        super().__init__(parent)
        self.path = str(Path(path).resolve())
        self.initial_slide = initial_slide
        self.autostart = autostart
        self.shortcuts = shortcuts
        self.commands = queue.Queue()
        self._command_lock = threading.Lock()
        self._native_commands = None
        self._stop_requested_at = None
        self._closed = False

    def navigate(self, command, slide=None):
        if command not in {"next", "previous", "goto", "stop", "start", "end_show",
                           "next_slide", "previous_slide", "stop_media", "play_media",
                           "pause_media", "resume_media", "set_shortcuts", "set_volume", "set_reading_badge"}:
            raise ValueError("Lệnh PowerPoint không hợp lệ.")
        with self._command_lock:
            if self._closed:
                return
            if command == 'stop' and self._stop_requested_at is None:
                self._stop_requested_at = time.monotonic()
            (self._native_commands if self._native_commands is not None else self.commands).put((command, slide))

    def stop(self):
        self.navigate("stop")

    def run(self):
        context = multiprocessing.get_context("spawn")
        commands, events = context.Queue(), context.Queue()
        process = context.Process(target=_office_session,
                                  args=(self.path, self.initial_slide, commands, events, self.autostart, self.shortcuts), daemon=True)
        stopping = None
        started = time.monotonic()
        ready = False
        try:
            process.start()
            with self._command_lock:
                self._native_commands = commands
                while not self.commands.empty():
                    commands.put(self.commands.get_nowait())
            while process.is_alive():
                if stopping is None:
                    stopping = self._stop_requested_at
                try:
                    state = events.get(timeout=0.1)
                    if "error" in state:
                        self.failed.emit(state["error"])
                    else:
                        ready = ready or bool(state.get("active") or state.get("opened"))
                        self.stateChanged.emit(state)
                except queue.Empty:
                    pass
                if stopping is not None and time.monotonic() - stopping > 5:
                    process.terminate()  # End only the private helper, never the user's Office process.
                    self.failed.emit("PowerPoint không phản hồi. Đã ngắt kết nối; có thể đóng cửa sổ trình chiếu.")
                    break
                if not ready and stopping is None and time.monotonic() - started > 45:
                    commands.put(("stop", None))
                    stopping = time.monotonic()
            process.join(timeout=2)
            while True:
                try:
                    state = events.get_nowait()
                    if "error" in state:
                        self.failed.emit(state["error"])
                except queue.Empty:
                    break
        except Exception:
            self.failed.emit("Chưa khởi động được trình chiếu. Hãy đóng BiliClass và mở lại bằng lối khởi động chính thức.")
        finally:
            with self._command_lock:
                self._native_commands = None
                self._closed = True
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
            commands.close()
            events.close()
            self.stateChanged.emit({"active": False, "slide": 0, "total": 0, "message": "Đã ngắt PowerPoint."})
