"""Check the selected recording once in a worker, never from a QML getter."""

from copy import deepcopy
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal, Slot

from .lesson_narration import audio_status


class StatusJob(QThread):
    def __init__(self, request, parent):
        super().__init__(parent)
        self.request = request
        self.cancel = Event()
        self.result = None

    def run(self):
        directory, lesson, voices = self.request
        try:
            self.result = audio_status(lesson, directory, voices, cancel=self.cancel)
        except InterruptedError:
            pass
        except Exception:
            self.result = {'status': 'unknown', 'ready': False, 'mode': 'none',
                           'label': 'Chưa kiểm tra được giọng đọc'}


class NarrationStatus(QObject):
    changed = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.worker = None
        self.request = None
        self.state = {}

    def refresh(self, directory, lesson, voices, *, force=False):
        # Appearance, title and speaker position do not change spoken content.
        fields = ('id', 'source', 'segments', 'narration', 'slide_speech', 'external_deck',
                  'narration_script', 'narration_silent', 'narration_image_text')
        snapshot = {key: lesson[key] for key in fields if key in lesson}
        request = (directory, snapshot, voices)
        if not force and request == self.request:
            return
        self.request = deepcopy(request)
        self.state = ({'status': 'checking', 'ready': False, 'mode': 'none',
                       'label': 'Đang kiểm tra giọng đọc'} if lesson else {})
        if self.worker is not None:
            self.worker.cancel.set()
        else:
            self._start()
        self.changed.emit()

    def _start(self):
        if not self.request or not self.request[1]:
            return
        self.worker = StatusJob(self.request, self)
        self.worker.finished.connect(self._finished)
        self.worker.start()

    @Slot()
    def _finished(self):
        worker = self.sender()
        if worker is None or worker is not self.worker:
            return
        self.worker = None
        current = worker.request is self.request and not worker.cancel.is_set()
        if current and worker.result is not None:
            self.state = worker.result
            self.changed.emit()
        worker.deleteLater()
        if not current:
            self._start()

    def shutdown(self):
        self.request = None
        if self.worker is not None:
            worker, self.worker = self.worker, None
            worker.cancel.set()
            worker.wait()
            worker.deleteLater()
