"""Live companion appearance with coalesced background persistence."""

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from .narration_preferences import store_choices
from .voice_controls import VoiceTask


def panel_size(mascot_size):
    return 'small' if mascot_size < 95 else 'large' if mascot_size >= 130 else 'standard'


class CompanionPreferences(QObject):
    changed = Signal()
    failed = Signal(str)
    persisted = Signal(object)

    def __init__(self, library, parent=None):
        super().__init__(parent)
        self.directory = library.directory
        saved = library.setting('companion_panel_opacity', 100)
        self.opacity = max(30, min(100, saved)) if type(saved) is int else 100
        from .narration_timing import PARAGRAPH_GAP_MS, select_gap, validated_gap

        self.reading_gap = validated_gap(library.setting('paragraph_gap_ms', PARAGRAPH_GAP_MS))
        select_gap(self.directory, self.reading_gap)
        self.worker = None
        self.pending = {}
        self._attempts = 0
        self._closed = False
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(350)
        self.timer.timeout.connect(self.flush)
        if parent is not None:
            parent.destroyed.connect(self.shutdown)

    def select_opacity(self, value):
        value = max(30, min(100, value))
        if self._closed or value == self.opacity:
            return
        self.opacity = value
        self.pending['companion_panel_opacity'] = value
        self._attempts = 0
        self.changed.emit()
        self.timer.start(350)

    def save_settings(self, choices):
        if self._closed:
            return
        self.pending.update(choices)
        self._attempts = 0
        self.flush()
        self.changed.emit()

    def select_reading_gap(self, value):
        from .narration_timing import select_gap, validated_gap

        value = validated_gap(value)
        if self._closed or value == self.reading_gap:
            return
        self.reading_gap = value
        select_gap(self.directory, value)
        self.pending['paragraph_gap_ms'] = value
        self._attempts = 0
        self.changed.emit()
        self.flush()

    @Slot()
    def flush(self):
        self.timer.stop()
        if self._closed or self.worker is not None or not self.pending:
            return
        choices, self.pending = self.pending, {}
        task = VoiceTask(lambda _: store_choices(self.directory, choices), self)
        task.choices = choices
        self.worker = task
        self.changed.emit()
        task.finished.connect(self._finished)
        task.start()

    @Slot()
    def _finished(self):
        task = self.sender()
        if task is not self.worker:
            return
        task.wait()
        self.worker = None
        if task.error:
            # A newer drag always wins over an earlier in-flight save.
            self.pending = {**task.choices, **self.pending}
            self._attempts += 1
            if self._attempts >= 3:
                self.failed.emit('Chưa lưu được cài đặt Mascot. Thư viện đang bận hoặc không ghi được; thử bấm Lưu lại.')
            elif not self._closed:
                self.timer.start(1000)
        else:
            self._attempts = 0
            self.persisted.emit(task.choices)
            if self.pending and not self._closed:
                self.timer.start(350)
        self.changed.emit()
        task.deleteLater()

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
                self.failed.emit('Chưa lưu được cài đặt trợ giảng; cấu hình đã lưu trước đó được giữ nguyên.')
            task.deleteLater()
