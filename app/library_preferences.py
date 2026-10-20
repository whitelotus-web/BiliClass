"""Immediate library view/sort with coalesced writes outside the Qt thread."""

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from .narration_preferences import store_choices
from .voice_controls import VoiceTask

OPTIONS = {'library_view': {'list', 'grid'}, 'lesson_order': {'created_desc', 'created_asc', 'updated_desc', 'title_asc'}}


class LibraryPreferences(QObject):
    changed = Signal()
    failed = Signal(str)

    def __init__(self, library, parent):
        super().__init__(parent)
        self.directory = library.directory
        self.values = {key: library.setting(key, default) for key, default in
                       (('library_view', 'list'), ('lesson_order', 'created_desc'))}
        self.pending, self.worker = {}, None
        self._closed, self._attempts = False, 0
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.flush)
        parent.destroyed.connect(self.shutdown)

    def select(self, key, value):
        if self._closed or value not in OPTIONS.get(key, set()) or self.values.get(key) == value:
            return
        self.values[key] = self.pending[key] = value
        self._attempts = 0
        self.changed.emit()
        self.timer.start(150)

    @Slot()
    def flush(self):
        if self._closed or self.worker is not None or not self.pending:
            return
        choices, self.pending = self.pending, {}
        self.worker = VoiceTask(lambda _: store_choices(self.directory, choices), self)
        self.worker.choices = choices
        self.worker.finished.connect(self._finished)
        self.worker.start()

    @Slot()
    def _finished(self):
        task = self.sender()
        if task is None or task is not self.worker:
            return
        self.worker = None
        if task.error:
            self.pending = {**task.choices, **self.pending}
            self._attempts += 1
            if self._attempts >= 3:
                self.failed.emit('Chưa lưu được cách xem thư viện. Lựa chọn trên màn hình vẫn được giữ.')
        task.deleteLater()
        if self.pending and not self._closed and self._attempts < 3:
            self.timer.start(500)

    @Slot()
    def shutdown(self):
        if self._closed:
            return
        self._closed = True
        self.timer.stop()
        if self.worker is not None:
            task, self.worker = self.worker, None
            task.wait()
            if task.error:
                self.pending = {**task.choices, **self.pending}
            task.deleteLater()
        if self.pending:
            choices, self.pending = self.pending, {}
            task = VoiceTask(lambda _: store_choices(self.directory, choices), self)
            task.start()
            task.wait()
            if task.error:
                self.failed.emit('Chưa lưu được cách xem thư viện cho lần mở sau.')
            task.deleteLater()
