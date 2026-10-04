"""Read-only PowerPoint control isolated from the desktop UI process."""

import hashlib
import multiprocessing
import queue
import re
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


def slideshow_handle(path):
    """Resolve the native window without relying on optional COM HWND members."""
    import win32gui

    matches = []

    def collect(hwnd, _):
        if (win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == "screenClass"
                and Path(path).stem.casefold() in win32gui.GetWindowText(hwnd).casefold()):
            matches.append(hwnd)

    win32gui.EnumWindows(collect, None)
    return matches[-1] if len(matches) == 1 else 0


def _office_session(path, initial_slide, commands, events):
    import psutil
    import pythoncom
    import win32com.client

    existing_office = any(
        (p.info["name"] or "").lower() == "powerpnt.exe" for p in psutil.process_iter(["name"])
    )
    pythoncom.CoInitialize()
    application = presentation = window = view = slide = None
    show_closed = False

    def progress(message):
        events.put({"active": False, "starting": True, "slide": 0, "total": 0, "message": message})

    try:
        progress("Đang kết nối PowerPoint…")
        application = win32com.client.DispatchEx("PowerPoint.Application")
        progress("Đang mở bài giảng trong PowerPoint…")
        presentation = application.Presentations.Open(path, ReadOnly=True, Untitled=False, WithWindow=False)
        presentation.SlideShowSettings.ShowType = 1  # ppShowTypeSpeaker: native full-screen slideshow.
        progress("Đang mở trình chiếu toàn màn hình…")
        window = presentation.SlideShowSettings.Run()
        try:
            hwnd = slideshow_handle(path)
        except Exception:
            hwnd = 0  # Presentation and narration still work without window positioning.
        view = window.View
        total = presentation.Slides.Count
        if 1 <= initial_slide <= total:
            view.GotoSlide(initial_slide)
        last = None
        while True:
            try:
                command, target = commands.get(timeout=0.15)
            except queue.Empty:
                command, target = None, None
            if command == "stop":
                break
            if command == "goto":
                if type(target) is int and 1 <= target <= total:
                    view.GotoSlide(target)
            elif command == "next":
                view.Next()  # Office handles animation builds before advancing the slide.
            elif command == "previous":
                view.Previous()
            pythoncom.PumpWaitingMessages()
            try:
                slide = view.Slide
                current = (slide.SlideIndex, slide.SlideID)
            except Exception:
                show_closed = True
                break  # User closed the slideshow; normal end of companion session.
            if current != last:
                events.put({"active": True, "slide": current[0], "slide_id": current[1], "total": total,
                            "hwnd": hwnd,
                            "message": f"PowerPoint · slide {current[0]}/{total}"})
                last = current
    except Exception as exc:
        events.put({"error": "Không thể điều khiển PowerPoint: " + str(exc)})
    finally:
        if window is not None and not show_closed:
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

    def __init__(self, path, initial_slide=1, parent=None):
        super().__init__(parent)
        self.path = str(Path(path).resolve())
        self.initial_slide = initial_slide
        self.commands = queue.Queue()

    def navigate(self, command, slide=None):
        if command not in {"next", "previous", "goto", "stop"}:
            raise ValueError("Lệnh PowerPoint không hợp lệ.")
        self.commands.put((command, slide))

    def stop(self):
        self.navigate("stop")

    def run(self):
        context = multiprocessing.get_context("spawn")
        commands, events = context.Queue(), context.Queue()
        process = context.Process(target=_office_session,
                                  args=(self.path, self.initial_slide, commands, events), daemon=True)
        stopping = None
        started = time.monotonic()
        ready = False
        try:
            process.start()
            while process.is_alive():
                try:
                    command = self.commands.get_nowait()
                    commands.put(command)
                    if command[0] == "stop" and stopping is None:
                        stopping = time.monotonic()
                except queue.Empty:
                    pass
                try:
                    state = events.get(timeout=0.1)
                    if "error" in state:
                        self.failed.emit(state["error"])
                    else:
                        ready = ready or bool(state.get("active"))
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
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
            commands.close()
            events.close()
            self.stateChanged.emit({"active": False, "slide": 0, "total": 0, "message": "Đã ngắt PowerPoint."})
