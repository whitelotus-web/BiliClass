"""Prepare narration after saving the lesson, outside the conversion worker."""

import json
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal, Slot

from . import speech
from .browser_audio import narration_tasks


class NarrationJob(QThread):
    progressed = Signal(object)

    def __init__(self, inspection, voices, directory, parent):
        super().__init__(parent)
        self.tasks, self.skipped, self.duplicates = narration_tasks(inspection, voices)
        self.rate, self.directory = voices["rate"], directory
        self.cancel, self.paused = Event(), Event()
        self.result = {}

    def run(self):
        complete = cached = failed = consecutive = 0
        try:
            for text, voice in self.tasks:
                while self.paused.is_set() and not self.cancel.is_set():
                    self.cancel.wait(.1)
                if self.cancel.is_set():
                    break
                try:
                    result = speech.synthesize_background(text, voice, self.rate, self.directory, self.cancel)
                    complete += 1
                    cached += bool(result.get("cached"))
                    consecutive = 0
                except InterruptedError:
                    break
                except Exception:
                    failed += 1
                    consecutive += 1
                self.result = {"complete": complete, "cached": cached, "failed": failed,
                               "total": len(self.tasks), "skipped": self.skipped,
                               "duplicates": self.duplicates}
                self.progressed.emit(dict(self.result))
                if consecutive >= 3:
                    break  # A missing/broken engine must not fail once per slide.
        finally:
            self.result = {"complete": complete, "cached": cached, "failed": failed,
                           "total": len(self.tasks), "skipped": self.skipped,
                           "duplicates": self.duplicates, "cancelled": self.cancel.is_set()}


class NarrationPreparation(QObject):
    changed = Signal()

    def __init__(self, directory, parent):
        super().__init__(parent)
        self.directory = directory
        self.worker = None
        self.pending = None
        self.state = {}
        self.path = None
        self.paused = False

    def start(self, lesson_id, inspection, voices, folder):
        request = lesson_id, inspection, dict(voices), folder
        if self.worker is not None:
            self.pending = request
            self.worker.cancel.set()
            return
        self.path = Path(folder) / "narration-progress.json"
        self.worker = NarrationJob(inspection, voices, self.directory, self)
        self.worker.paused.set() if self.paused else self.worker.paused.clear()
        self.state = {"lesson_id": lesson_id, "running": True, "complete": 0, "failed": 0,
                      "voice": voices.get("voice", ""), "rate": voices["rate"],
                      "total": len(self.worker.tasks), "message": "Giọng đọc đang được chuẩn bị tự động ở nền. Có thể xem bài ngay."}
        self.worker.progressed.connect(self._progress)
        self.worker.finished.connect(self._finished)
        self._persist()
        self.changed.emit()
        self.worker.start()

    def pause(self, paused):
        self.paused = bool(paused)
        if self.worker is not None:
            self.worker.paused.set() if paused else self.worker.paused.clear()

    @Slot(object)
    def _progress(self, result):
        if self.sender() is not self.worker:
            return
        self.state.update(result, message=f"Giọng đọc: {result['complete']}/{result['total']} đoạn · tự chuẩn bị ở nền.")
        self._persist()
        self.changed.emit()

    @Slot()
    def _finished(self):
        worker = self.sender()
        if worker is not self.worker:
            return
        self.state.update(worker.result, running=False)
        if worker.result["cancelled"]:
            self.state["message"] = "Đã dừng chuẩn bị nền; âm thanh đã tạo được giữ lại. Giọng đọc vẫn được tạo khi dùng."
        elif worker.result["failed"] or worker.result["skipped"]:
            self.state["message"] = "Một số lời đọc chưa tạo được. PowerPoint đã lưu; kiểm tra giọng đọc và nội dung."
        else:
            self.state["message"] = f"Đã chuẩn bị {worker.result['complete']}/{worker.result['total']} đoạn giọng đọc."
        self.worker = None
        self._persist()
        self.changed.emit()
        worker.deleteLater()
        if self.pending is not None:
            request, self.pending = self.pending, None
            self.start(*request)

    def _persist(self):
        try:
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps({"version": 1, **self.state}, ensure_ascii=False), encoding="utf-8")
            temporary.replace(self.path)
        except OSError:
            pass  # An optional cache checkpoint cannot invalidate a saved lesson.

    def cancel(self):
        self.pending = None
        if self.worker is not None:
            self.worker.cancel.set()

    def shutdown(self):
        self.cancel()
        if self.worker is not None:
            self.worker.wait()  # Finish the current CPU call; never terminate the model.
