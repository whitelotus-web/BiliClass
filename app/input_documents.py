"""Latest-choice-wins file validation, without filesystem work on the GUI thread."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from .conversion_input import document_selection
from .jobs import Job


class InputDocuments(QObject):
    changed = Signal()
    selected = Signal('QVariantMap', str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.pending = None
        self.generation = 0

    @Property(bool, notify=changed)
    def busy(self):
        return self.pending is not None or bool(self.worker and self.worker.generation == self.generation)

    @Slot('QVariantList')
    def select(self, urls):
        self.generation += 1
        self.pending = (self.generation, list(urls))
        self.changed.emit()
        self._start()

    def _start(self):
        if self.worker is not None or self.pending is None:
            return
        generation, urls = self.pending
        self.pending = None
        worker = Job(lambda: document_selection(urls), self)
        worker.generation = generation
        self.worker = worker
        worker.completed.connect(self._completed)
        worker.finished.connect(self._finished)
        worker.start()

    @Slot(object, str)
    def _completed(self, result, error):
        if self.worker.generation == self.generation:
            self.selected.emit(result or {'valid': False}, error)

    @Slot()
    def _finished(self):
        worker, self.worker = self.worker, None
        worker.deleteLater()
        self._start()
        self.changed.emit()

    @Slot()
    def clear(self):
        self.generation += 1
        self.pending = None
        self.changed.emit()

    def shutdown(self):
        self.clear()
        if self.worker is not None:
            self.worker.wait()
