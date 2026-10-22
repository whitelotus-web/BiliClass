"""Read-only queue input details and latest-choice-wins slide preview."""

from threading import Event

from PySide6.QtCore import Property, QObject, Signal, Slot

from .input_documents import InputDocuments
from .jobs import Job


def input_details(rows, cancel):
    from xml.etree import ElementTree
    from zipfile import BadZipFile, ZipFile

    from .conversion_input import local_document

    details = {}
    for row in rows:
        if cancel.is_set():
            break
        try:
            path = local_document(row['url'])
            if path.suffix.lower() != '.pptx':
                raise ValueError('Chỉ nhận file PowerPoint (.pptx).')
            with ZipFile(path) as archive:
                entry = archive.getinfo('ppt/presentation.xml')
                if entry.file_size > 4_000_000:
                    raise ValueError('Danh sách slide trong file vượt giới hạn.')
                root = ElementTree.fromstring(archive.read(entry))
            ns = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
            total = len(root.findall(ns+'sldIdLst/'+ns+'sldId'))
            if not total:
                raise ValueError('PowerPoint chưa có slide.')
            details[row['id']] = {'total': total, 'bytes': path.stat().st_size}
        except (KeyError, BadZipFile, ElementTree.ParseError):
            details[row['id']] = {'error': 'Không đọc được PowerPoint. Chọn lại file .pptx hợp lệ.'}
        except (OSError, ValueError) as exc:
            details[row['id']] = {'error': str(exc)}
    return details


class BatchInputs(QObject):
    changed = Signal()

    def __init__(self, queue):
        super().__init__(queue)
        self.queue = queue
        self.documents = InputDocuments(self)
        self.documents.directory = queue.bridge.library.directory
        self.identity = self.selected_id = ''
        self.details = {}
        self.worker = self.pending = None
        self.cancel = Event()
        self.closed = False
        queue.changed.connect(self.sync)
        queue.destroyed.connect(self.shutdown)

    @Property(QObject, constant=True)
    def previewer(self):
        return self.documents

    @Property('QVariantMap', notify=changed)
    def state(self):
        rows = [{**row, **self.details.get(row['id'], {})} for row in self.queue.data.get('rows', [])]
        return {'rows': rows, 'selected_id': self.selected_id,
                'selected': next((row for row in rows if row['id'] == self.selected_id), {})}

    @Slot()
    def sync(self):
        data = self.queue.data
        active = bool(data.get('rows')) and data.get('phase') == 'draft' and not self.queue.running and self.queue.state['shown']
        if not active:
            self.cancel.set()
            self.pending = None
            self.identity = ''
            if self.selected_id:
                self.selected_id = ''
                self.documents.clear()
                self.changed.emit()
            return
        if data['id'] != self.identity:
            self.cancel.set()
            self.identity = data['id']
            self.details = {}
            self.selected_id = ''
            self.pending = (self.identity, [dict(row) for row in data['rows']])
            self._start()
        if self.selected_id not in {row['id'] for row in data['rows']}:
            self.select(data['rows'][0]['id'])
        self.changed.emit()

    def _start(self):
        if self.closed or self.worker is not None or not self.pending:
            return
        identity, rows = self.pending
        self.pending = None
        cancel = self.cancel = Event()
        worker = Job(lambda: input_details(rows, cancel), self)
        worker.identity = identity
        self.worker = worker
        worker.completed.connect(self._completed)
        worker.finished.connect(self._finished)
        worker.start()

    @Slot(object, str)
    def _completed(self, result, error):
        if not self.closed and self.worker.identity == self.identity:
            self.details = result or {}
            self.changed.emit()

    @Slot()
    def _finished(self):
        worker, self.worker = self.worker, None
        worker.deleteLater()
        self._start()

    @Slot(str)
    def select(self, identity):
        if self.closed or self.queue.data.get('phase') != 'draft' or self.queue.running:
            return
        row = next((row for row in self.queue.data.get('rows', []) if row['id'] == identity), None)
        if row is None or identity == self.selected_id:
            return
        self.selected_id = identity
        self.documents.select([row['url']])
        self.changed.emit()

    def shutdown(self):
        self.closed = True
        self.cancel.set()
        self.pending = None
        self.documents.shutdown()
        if self.worker is not None:
            self.worker.wait()
