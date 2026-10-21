"""Latest-choice-wins file validation, without filesystem work on the GUI thread."""

import hashlib
from threading import Event

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from .conversion_input import document_selection
from .jobs import Job


class InputDocuments(QObject):
    changed = Signal()
    previewChanged = Signal()
    selected = Signal('QVariantMap', str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.pending = None
        self.generation = 0
        self.preview_worker = self.preview_pending = None
        self.preview_generation = 0
        self.preview_cancel = Event()
        self.preview_state = {}
        self.selected_url = ''
        self.directory = getattr(getattr(parent, 'library', None), 'directory', None)
        self.closed = False
        if parent is not None:
            parent.destroyed.connect(self.shutdown)

    @Property('QVariantMap', notify=previewChanged)
    def preview(self):
        return dict(self.preview_state)

    @Property(bool, notify=changed)
    def busy(self):
        return self.pending is not None or bool(self.worker and self.worker.generation == self.generation)

    @Slot('QVariantList')
    def select(self, urls):
        self._clear_preview()
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
            if (self.worker.generation == self.generation and not error and result and result.get('valid')
                    and result.get('url', '').lower().endswith('.pptx') and self.directory):
                self.selected_url = result['url']
                self.retryPreview()

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
        self._clear_preview()
        self.changed.emit()

    def _clear_preview(self):
        self.preview_generation += 1
        self.preview_cancel.set()
        self.preview_pending = None
        self.preview_state = {}
        self.selected_url = ''
        self.previewChanged.emit()

    @Slot()
    def retryPreview(self):
        self._request_preview(self.preview_state.get('slide', 1))

    @Slot(int)
    def showSlide(self, number):
        if number < 1 or number > self.preview_state.get('total', 0):
            return
        self._request_preview(number)

    def _request_preview(self, number):
        if not self.selected_url or self.closed:
            return
        self.preview_generation += 1
        self.preview_cancel.set()
        self.preview_pending = (self.preview_generation, self.selected_url, number)
        self.preview_state = {**self.preview_state, 'busy': True, 'error': '', 'slide': number}
        self.previewChanged.emit()
        self._start_preview()

    def _start_preview(self):
        if self.closed or self.preview_worker or not self.preview_pending:
            return
        generation, url, number = self.preview_pending
        self.preview_pending = None
        cancel = self.preview_cancel = Event()
        worker = Job(lambda: input_preview(url, self.directory, cancel, number), self)
        worker.generation = generation
        self.preview_worker = worker
        worker.completed.connect(self._preview_completed)
        worker.finished.connect(self._preview_finished)
        worker.start()

    @Slot(object, str)
    def _preview_completed(self, result, error):
        if not self.closed and self.preview_worker.generation == self.preview_generation:
            self.preview_state = {**self.preview_state, **(result or {}), 'busy': False, 'error': error}
            if error:
                self.preview_state['image'] = ''
            self.previewChanged.emit()

    @Slot()
    def _preview_finished(self):
        worker, self.preview_worker = self.preview_worker, None
        worker.deleteLater()
        self._start_preview()

    def shutdown(self):
        self.closed = True
        self.clear()
        if self.worker is not None:
            self.worker.wait()
        if self.preview_worker is not None:
            self.preview_worker.wait()


def input_preview(url, directory, cancel, number=1):
    import json
    from datetime import date
    from pathlib import Path

    from pptx import Presentation

    from .conversion_input import local_document
    from .powerpoint_review import render_preview_pages
    from .slide_fingerprint import environment_key
    from .slide_preview import stamp

    path = local_document(url)
    before = stamp(path)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    total = len(Presentation(path).slides)
    if not total:
        raise ValueError('PowerPoint chưa có slide.')
    if not 1 <= number <= total:
        raise ValueError('Slide xem trước không hợp lệ.')
    if cancel.is_set():
        raise InterruptedError('Đã dừng xem trước.')
    folder = Path(directory)/'temp/lesson-preview-images'/digest[:24]
    image = folder/f'slide-{number}.png'
    reusable = False
    try:
        index = json.loads((folder/'preview-cache.json').read_text(encoding='utf-8'))
        row = index['slides'][str(number)]
        content = image.read_bytes()
        reusable = (index.get('version') == 3 and index.get('sha256') == digest
                    and row.get('environment') == environment_key()
                    and (not row.get('date_sensitive', True) or row.get('rendered_date') == date.today().isoformat())
                    and content.startswith(b'\x89PNG\r\n\x1a\n')
                    and hashlib.sha256(content).hexdigest() == row.get('image_sha256'))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    if not reusable:
        pages = [number] + [n for n in (number+1, number-1) if 1 <= n <= total]
        folder, _ = render_preview_pages(path, pages, directory, digest, cancel)
    if cancel.is_set():
        raise InterruptedError('Đã dừng xem trước.')
    if stamp(path) != before:
        raise ValueError('PowerPoint vừa thay đổi. Chọn lại tệp để xem bản mới.')
    return {'image': QUrl.fromLocalFile(str(folder/f'slide-{number}.png')).toString(), 'total': total, 'slide': number}
