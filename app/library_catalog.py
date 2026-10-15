"""Publish library summaries without scanning WAV files on the Qt thread."""

from contextlib import closing
from threading import Event

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from .library import Library, timestamp
from .lesson_narration import audio_status
from .speech import voice_settings


class CatalogJob(QThread):
    metadata = Signal(object)

    def __init__(self, directory, parent):
        super().__init__(parent)
        self.directory = directory
        self.cancel = Event()
        self.result = None
        self.error = False

    def run(self):
        try:
            with closing(Library.read_only(self.directory)) as library:
                active = library.list_lessons(verify_audio=False)
                trash = library.list_lessons(trash=True, verify_audio=False)
                # Never mutate the rows already published to the GUI.
                self.metadata.emit((active, trash))
                voices = voice_settings(library)
                verified = []
                for row in active:
                    if self.cancel.is_set():
                        return
                    status = audio_status(library.get(row['id']), library.directory, voices, cancel=self.cancel)
                    verified.append({**row, 'narration': status})
                self.result = verified, trash
        except InterruptedError:
            pass
        except Exception:
            self.error = True
            if 'active' in locals() and 'trash' in locals():
                unknown = {'status': 'unknown', 'mode': 'none', 'ready': False,
                           'label': 'Chưa kiểm tra được giọng đọc'}
                self.result = [{**row, 'narration': dict(unknown)} for row in active], trash


class LibraryCatalog(QObject):
    changed = Signal()

    def __init__(self, library, parent):
        super().__init__(parent)
        self.library = library
        self.worker = None
        self._active = []
        self._trash = []
        self._revision = None
        self._pending = False
        self._closed = False
        parent.destroyed.connect(self.shutdown)
        QTimer.singleShot(0, self.refresh)

    def rows(self, order='updated_desc', *, trash=False):
        rows = self._trash if trash else self._active
        field = 'updated_at' if order == 'updated_desc' else 'created_at'
        return sorted(rows, key=lambda row: (timestamp(row.get(field)), row['id']), reverse=order != 'created_asc')

    @Slot()
    def refresh(self, force=False):
        if self._closed:
            return
        if self.library._closed:
            self.shutdown()
            return
        # SQLite's counters are cheap. Our connection's total_changes catches
        # local edits; data_version also catches completed worker imports.
        revision = (self.library.db.total_changes, self.library.db.execute('PRAGMA data_version').fetchone()[0])
        if revision == self._revision and not force:
            return
        self._revision = revision
        if self.worker is not None:
            self._pending = True
            self.worker.cancel.set()
            return
        self._start()

    def _start(self):
        self._pending = False
        self.worker = CatalogJob(self.library.directory, self)
        self.worker.metadata.connect(self._metadata)
        self.worker.finished.connect(self._finished)
        self.worker.start()

    @Slot(object)
    def _metadata(self, result):
        if self.sender() is self.worker and not self._pending and not self._closed:
            self._active, self._trash = result
            self.changed.emit()

    @Slot()
    def _finished(self):
        worker = self.sender()
        if worker is not self.worker:
            return
        self.worker = None
        if not self._pending and not self._closed and worker.result is not None:
            self._active, self._trash = worker.result
            self.changed.emit()
        worker.deleteLater()
        if self._pending and not self._closed:
            self._start()

    @Slot()
    def shutdown(self):
        self._closed = True
        self._pending = False
        if self.worker is not None:
            worker, self.worker = self.worker, None
            worker.cancel.set()
            worker.wait()
            worker.deleteLater()

    def replace_library(self, library):
        self.shutdown()
        self.library = library
        self._active, self._trash = [], []
        self._revision = None
        self._closed = False
        self.changed.emit()
        self.refresh()
