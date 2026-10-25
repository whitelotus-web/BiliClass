"""Publish library summaries without scanning WAV files on the Qt thread."""

from contextlib import closing
from threading import Event

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from .lesson_narration import library_audio_status as audio_status
from .lesson_state import summarize_state
from .library import Library, timestamp
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
                    lesson = library.get(row['id'])
                    status = audio_status(lesson, library.directory, voices, cancel=self.cancel)
                    verified.append({**row, 'narration': status, 'workflow': summarize_state(lesson, status),
                                     'library_product': row.get('library_product', True) or status.get('ready', False)})
                self.result = verified, trash
        except InterruptedError:
            pass
        except Exception:
            self.error = True
            if 'active' in locals() and 'trash' in locals():
                unknown = {'status': 'unknown', 'mode': 'none', 'ready': False,
                           'label': 'Chưa kiểm tra được giọng đọc'}
                self.result = [{**row, 'narration': dict(unknown), 'workflow': {
                    **row.get('workflow', {}), 'audio_ready': False,
                    'audio_label': unknown['label'], 'audio_complete': 0, 'audio_total': 0}} for row in active], trash


class WordCatalogJob(QThread):
    def __init__(self, directory, parent):
        super().__init__(parent)
        self.directory, self.result = directory, None

    def run(self):
        from .library_documents import word_rows

        try:
            self.result = word_rows(self.directory), word_rows(self.directory, trash=True)
        except (OSError, ValueError):
            pass  # A Word catalog problem must not hide the PowerPoint library.


class LibraryCatalog(QObject):
    changed = Signal()

    def __init__(self, library, parent):
        super().__init__(parent)
        self.library = library
        self.worker = None
        self.word_worker, self._word_pending = None, False
        self._active = []
        self._trash = []
        self._words, self._word_trash = [], []
        self._revision = None
        self._pending = False
        self._closed = False
        from .narration_status import NarrationStatus

        self.selected_narration = NarrationStatus(self)
        parent.destroyed.connect(self.shutdown)
        QTimer.singleShot(0, self.refresh)
        QTimer.singleShot(0, self.refresh_words)

    def rows(self, order='updated_desc', *, trash=False, include_sources=False):
        rows = self._trash if trash else self._active
        if not trash and not include_sources:
            rows = [row for row in rows if row.get('library_product', True)]
        if order == 'title_asc':
            from .library_view import folded
            return sorted(rows, key=lambda row: (folded(row['title']), row['id']))
        field = 'updated_at' if order == 'updated_desc' else 'created_at'
        return sorted(rows, key=lambda row: (timestamp(row.get(field)), row['id']), reverse=order != 'created_asc')

    def documents(self, order='updated_desc', *, trash=False):
        rows = [{**row, 'document_type': 'powerpoint'} for row in self.rows(order, trash=trash)]
        rows += self._word_trash if trash else self._words
        if order == 'title_asc':
            from .library_view import folded

            return sorted(rows, key=lambda row: (folded(row['title']), row['id']))
        field = 'updated_at' if order == 'updated_desc' else 'created_at'
        return sorted(rows, key=lambda row: (timestamp(row.get(field)), row['id']), reverse=order != 'created_asc')

    @Slot()
    def refresh_words(self):
        if self._closed or self.library._closed:
            return
        if self.word_worker is not None:
            self._word_pending = True
            return
        self._word_pending = False
        self.word_worker = WordCatalogJob(self.library.directory, self)
        self.word_worker.finished.connect(self._words_finished)
        self.word_worker.start()

    @Slot()
    def _words_finished(self):
        worker = self.sender()
        if worker is None or worker is not self.word_worker:
            return
        self.word_worker = None
        if not self._closed and not self._word_pending and worker.result is not None:
            self._words, self._word_trash = worker.result
            self.changed.emit()
        worker.deleteLater()
        if self._word_pending and not self._closed:
            self.refresh_words()

    @Slot()
    def refresh(self, force=False):
        if self._closed:
            return
        if self.library._closed:
            self.shutdown()
            return
        # Lesson-only local writes plus data_version for external imports.
        revision = (self.library.catalog_revision(), self.library.setting('voice_options', None),
                    self.library.setting('voice_vi', ''), self.library.setting('voice_rate', 0))
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
        if worker is None or worker is not self.worker:
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
        self._word_pending = False
        self.selected_narration.shutdown()
        if self.word_worker is not None:
            worker, self.word_worker = self.word_worker, None
            worker.wait()
            worker.deleteLater()
        if self.worker is not None:
            worker, self.worker = self.worker, None
            worker.cancel.set()
            worker.wait()
            worker.deleteLater()

    def replace_library(self, library):
        self.shutdown()
        self.library = library
        self._active, self._trash = [], []
        self._words, self._word_trash = [], []
        self._revision = None
        self._closed = False
        self.changed.emit()
        self.refresh()
        self.refresh_words()
