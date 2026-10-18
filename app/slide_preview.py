"""Latest-request preview queue; verify a deck once, reuse exact rendered PNGs."""

import copy
import hashlib
import json
import os
from datetime import date
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QUrl, Signal, Slot


@lru_cache(maxsize=1)
def _windows_attributes():
    import ctypes as c
    from ctypes import wintypes as w

    class BasicInfo(c.Structure):
        _fields_ = [
            ("created", c.c_longlong),
            ("accessed", c.c_longlong),
            ("written", c.c_longlong),
            ("changed", c.c_longlong),
            ("attributes", w.DWORD),
        ]

    kernel = c.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE]
    kernel.CreateFileW.restype = w.HANDLE
    kernel.GetFileInformationByHandleEx.argtypes = [w.HANDLE, c.c_int, w.LPVOID, w.DWORD]
    kernel.GetFileInformationByHandleEx.restype = w.BOOL
    kernel.DeviceIoControl.argtypes = [w.HANDLE, w.DWORD, w.LPVOID, w.DWORD, w.LPVOID, w.DWORD,
                                      c.POINTER(w.DWORD), w.LPVOID]
    kernel.DeviceIoControl.restype = w.BOOL
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.CloseHandle.restype = w.BOOL
    return kernel, BasicInfo


def stamp(path):
    stat = Path(path).stat()
    change = stat.st_ctime_ns
    if os.name == "nt":
        import ctypes as c
        from ctypes import wintypes as w

        kernel, Info = _windows_attributes()
        handle = kernel.CreateFileW(str(Path(path).absolute()), 0x80, 7, None, 3, 0x02000000, None)
        if handle != c.c_void_p(-1).value:
            try:
                info = Info()
                if kernel.GetFileInformationByHandleEx(handle, 0, c.byref(info), c.sizeof(info)):
                    # ChangeTime can repeat for two writes within one clock
                    # tick. NTFS's USN changes even when mtime is restored.
                    # Filesystems without a journal use an exact hash.
                    record, count = c.create_string_buffer(4096), w.DWORD()
                    ok = kernel.DeviceIoControl(handle, 0x000900EB, None, 0, record, len(record), c.byref(count), None)
                    version = int.from_bytes(record.raw[4:6], 'little')
                    offset = 24 if version == 2 else 40 if version == 3 else None
                    usn = int.from_bytes(record.raw[offset:offset+8], 'little') if ok and offset is not None and count.value >= offset+8 else 0
                    change = (info.changed, usn) if usn else hashlib.sha256(Path(path).read_bytes()).hexdigest()
                else:
                    change = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            finally:
                kernel.CloseHandle(handle)
        else:
            change = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return stat.st_size, stat.st_mtime_ns, change, stat.st_ino


class PreviewSession:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.identity = None
        self.file_stamp = None
        self.verified_images = {}
        self.indexes = []
        self.environment = None

    def render(self, lesson, result, number, *, neighbours=True, cached_only=False):
        from .quick_conversion import verify_preview
        from .slide_fingerprint import environment_key

        path = Path(result["path"])
        identity = (lesson["id"], lesson["revision"], result["sha256"], str(path))
        current = stamp(path)
        if self.identity != identity or self.file_stamp != current:
            verify_preview(lesson, result, self.directory)
            if stamp(path) != current:
                raise ValueError("Bài giảng vừa thay đổi; mở lại bài để xem bản mới.")
            self.identity, self.file_stamp = identity, current
            self.verified_images = {}
            self.environment = environment_key()
            self.indexes = []
            digest = result["sha256"]
            for folder, name in [
                ("slide-quality", "render-cache.json"),
                ("lesson-preview-images", "preview-cache.json"),
            ]:
                directory = self.directory / "temp" / folder / digest[:24]
                try:
                    index = json.loads((directory / name).read_text(encoding="utf-8"))
                    if index.get("sha256") == digest and index.get("version") == 3:
                        self.indexes.append((directory, index["slides"]))
                except (OSError, ValueError, KeyError, TypeError):
                    pass
        for directory, entries in self.indexes:
            item = entries.get(str(number), {})
            image = directory / f"slide-{number}.png"
            try:
                if item.get("environment") != self.environment:
                    continue
                if item.get('date_sensitive', True) and item.get('rendered_date') != date.today().isoformat():
                    continue
                image_stamp = stamp(image)
                known = self.verified_images.get(str(image))
                if known != image_stamp:
                    data = image.read_bytes()
                    if not data.startswith(b"\x89PNG\r\n\x1a\n") or hashlib.sha256(
                        data
                    ).hexdigest() != item.get("image_sha256"):
                        continue
                    self.verified_images[str(image)] = image_stamp
                return str(image)
            except OSError:
                continue
        if cached_only:
            raise LookupError("Chưa có ảnh slide trong bộ nhớ đệm.")
        from .powerpoint_review import render_preview_pages

        pages = [number] + ([p for p in (number + 1, number - 1) if 1 <= p <= result["total"]] if neighbours else [])
        folder, index = render_preview_pages(path, pages, self.directory, result["sha256"])
        self.indexes.append((folder, index["slides"]))
        if stamp(path) != self.file_stamp:
            self.identity = None
            raise ValueError("Bài giảng vừa thay đổi; mở lại bài để xem bản mới.")
        return str(folder / f"slide-{number}.png")


class PreviewJob(QThread):
    def __init__(self, session, request, parent):
        super().__init__(parent)
        self.session, self.request = session, request
        self.result = {}

    def run(self):
        lesson, result, number = self.request
        self.result = {"lesson_id": lesson["id"], "revision": lesson["revision"], "slide": number}
        try:
            image = self.session.render(lesson, result, number)
            self.result["image"] = QUrl.fromLocalFile(image).toString()
        except Exception as exc:
            # Keep a useful local diagnostic instead of losing every Office /
            # frozen-runtime failure behind the same empty preview message.
            import traceback
            folder = self.session.directory / "temp" / "preview-errors"
            try:
                folder.mkdir(parents=True, exist_ok=True)
                (folder / (result["lesson_id"] + ".json")).write_text(json.dumps({
                    "slide": number, "type": type(exc).__name__, "message": str(exc),
                    "traceback": traceback.format_exc()}, ensure_ascii=False), encoding="utf-8")
            except OSError:
                pass
            self.result["error"] = "Chưa xem được trang này. Bạn có thể mở bài bằng PowerPoint."


class SlidePreview(QObject):
    ready = Signal(object)
    changed = Signal()

    def __init__(self, directory, parent=None):
        super().__init__(parent)
        self.session = PreviewSession(directory)
        self.worker = None
        self.pending = None
        self.latest = None

    def start(self, lesson, result, number):
        request = (copy.deepcopy(lesson), dict(result), number)
        self.latest = (lesson["id"], lesson["revision"], number)
        if self.worker is not None:
            self.pending = request
            return
        self.worker = PreviewJob(self.session, request, self)
        self.worker.finished.connect(self._finished)
        self.changed.emit()
        self.worker.start()

    @Slot()
    def _finished(self):
        worker = self.worker
        result = worker.result
        self.worker = None
        worker.deleteLater()
        if self.latest == (result["lesson_id"], result["revision"], result["slide"]):
            self.ready.emit(result)
        if self.pending is not None:
            request, self.pending = self.pending, None
            self.start(*request)
        else:
            self.changed.emit()

    def shutdown(self):
        self.pending = None
        self.latest = None
        if self.worker is not None:
            self.worker.wait()
