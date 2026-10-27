"""Qt controller for the Word-only, whole-document queue."""

import copy
from pathlib import Path
from time import monotonic

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from . import word_batch_jobs as batches
from . import word_jobs as jobs


class WordBatch(QObject):
    changed = Signal()
    progressed = Signal(object)

    def __init__(self, documents):
        super().__init__(documents)
        self.documents, self.bridge = documents, documents.bridge
        self.data = {}
        self._running = self._stopping = False
        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self.changed.emit)
        self._progress_timer = QTimer(self)
        self._progress_timer.setSingleShot(True)
        self._progress_timer.setInterval(40)
        self._progress_timer.timeout.connect(self.changed.emit)
        self.progressed.connect(self._progress)
        identity = self.bridge.library.setting('last_word_batch', '')
        if identity:
            try:
                data = batches.load(self.bridge.library.directory, identity)
                if data['phase'] != 'dismissed':
                    data.pop('clock_monotonic', None)
                    if data['phase'] == 'running':
                        data.update(phase='paused', message='Lượt trước chưa xong. Bấm Tiếp tục; các bài đã làm được giữ.')
                        for row in data['rows']:
                            if row['status'] == 'running':
                                row['status'] = 'waiting'
                    self.data = data
            except (OSError, ValueError, TypeError, KeyError):
                self.bridge.logger.info('Word queue unavailable; document checkpoints remain in the library.')

    @Property('QVariantMap', notify=changed)
    def state(self):
        snapshot = copy.deepcopy(self.data)
        rows = snapshot.get('rows', [])
        counts = {status: sum(row['status'] == status for row in rows) for status in batches.STATUSES}
        age = max(0, monotonic() - snapshot.get('clock_monotonic', monotonic())) if self._running else 0
        snapshot['elapsed_seconds'] = snapshot.get('elapsed_seconds', 0) + age
        for row in rows:
            if row['status'] == 'running':
                row['elapsed_seconds'] = row.get('elapsed_seconds', 0) + age
        complete = bool(rows) and counts['done'] == len(rows) and not self._running
        return {**snapshot, 'total': len(rows), 'shown': True, 'running': self._running,
            'stopping': self._stopping, 'counts': counts, 'complete': complete,
            'canResume': bool(counts['waiting']) and not self._running,
            'canRetry': bool(counts['failed']) and not self._running}

    def _error(self, message):
        self.documents._show_error(message)
        self.bridge.inform(message, True, refresh=False)

    @Slot(result=bool)
    def clear(self):
        if not self.documents.available():
            return False
        if not self.data:
            return True
        try:
            batches.discard(self.bridge.library.directory, self.data)
            self.bridge.library.set_setting('last_word_batch', '')
        except (OSError, ValueError) as exc:
            self._error(str(exc))
            return False
        self.data = {}
        self.changed.emit()
        return True

    @Slot('QVariantList')
    def selectFiles(self, urls):
        if not self.documents._can_change_input():
            return
        try:
            data = batches.selection(list(urls))
            batches.persist(self.bridge.library.directory, data)
            if not self.clear():
                return
            self.bridge.library.set_setting('last_word_batch', data['id'])
        except (OSError, ValueError) as exc:
            self._error(str(exc))
            return
        self.documents._dismiss_source()
        self.data = data
        self.changed.emit()

    @Slot(str)
    def remove(self, identity):
        if not self.documents.available() or self.data.get('phase') != 'draft':
            return
        rows = [row for row in self.data['rows'] if row['id'] != identity]
        if not rows:
            self.clear()
            return
        data = copy.deepcopy(self.data)
        data['rows'] = rows
        try:
            from .batch_jobs import queue_lock

            with queue_lock(self.bridge.library.directory):
                batches.check_revision(self.bridge.library.directory, data)
                batches.persist(self.bridge.library.directory, data)
            self.data = data
            self.changed.emit()
        except (OSError, ValueError) as exc:
            self._error(str(exc))

    @Slot('QVariantMap', str, str)
    def start(self, formatting, subject, grade):
        if not self.documents._can_change_input() or not self.data:
            return
        if self.data['phase'] == 'draft':
            from .translation_provider import require_credentials, snapshot
            try:
                formatting = jobs.options_for(formatting)
                subject, grade = str(subject).strip()[:120], str(grade).strip()[:80]
                if not subject or grade not in {str(number) for number in range(1, 13)}:
                    raise ValueError('Chọn môn học và khối lớp trước khi chuyển đổi.')
                route = snapshot(self.bridge.library.directory, include_fallback=True)
                if formatting['mode'] != 'keywords':
                    require_credentials(self.bridge.library.directory, route['translation_provider'], route)
                self.data['options'] = dict(formatting=formatting, subject=subject, grade=grade, route=route)
                self.data['summary'] = 'Dịch toàn bộ · ' + subject + ' · Lớp ' + grade
            except (OSError, ValueError) as exc:
                self._error(str(exc))
                return
        self._start(retry=self.state['canRetry'])

    @Slot()
    def resume(self):
        if self.documents.available() and self.state['canResume']:
            self._start(retry=self.state['canRetry'])

    @Slot()
    def retryFailed(self):
        if self.documents.available() and self.state['canRetry']:
            self._start(retry=True)

    def _start(self, retry=False):
        if not self.data.get('options') or not self.documents.available():
            return
        self._running, self._stopping = True, False
        self.data.pop('clock_monotonic', None)
        self.documents._attention = ''
        self.documents.changed.emit()
        self.bridge.stopSpeech()
        self._clock.start()
        self.changed.emit()
        directory = self.bridge.library.directory
        data = copy.deepcopy(self.data)

        def work():
            try:
                result = batches.run(directory, data, self.bridge.cancel_event, self.progressed.emit, retry=retry)
                return dict(queue=result, library=jobs.catalog(directory))
            except Exception as exc:
                try:
                    result = batches.load(directory, data['id'])
                except (OSError, ValueError, KeyError, TypeError):
                    result = data
                result.update(phase='paused', message=str(exc))
                return dict(queue=result, error=str(exc))

        def finished(result):
            self._clock.stop()
            self._progress_timer.stop()
            self._running = self._stopping = False
            self.data = result.get('queue', self.data)
            if not result.get('queue'):
                self.data.update(phase='paused', message=result.get('error', 'Chưa hoàn tất hàng đợi Word.'))
            self.documents._library = result.get('library', self.documents._library)
            self.documents.libraryChanged.emit()
            self.changed.emit()
            self.documents.changed.emit()
            self.bridge._catalog.refresh()
            self.bridge.googleSettings.refresh()
            counts = self.state['counts']
            self.bridge.inform(f"Word: {counts['done']}/{len(self.data.get('rows', []))} bài hoàn tất"
                + (f" · {counts['failed']} bài cần thử lại" if counts['failed'] else ''), refresh=False)

        self.bridge.launch(work, finished, message='Đang chuyển đổi Word · xử lý lần lượt từng file…')
        self.bridge.worker.word_task = True

    @Slot(object)
    def _progress(self, value):
        if self._running and value.get('id') == self.data.get('id'):
            self.data = value
            if not self._progress_timer.isActive():
                self._progress_timer.start()

    @Slot()
    def stop(self):
        if self._running:
            self._stopping = True
            self.bridge.cancel_event.set()
            self.changed.emit()

    @Slot(str)
    def openResult(self, identity):
        if self.documents.available():
            row = next((row for row in self.data.get('rows', []) if row['id'] == identity), {})
            if row.get('word_id'):
                self.documents.openOutput(row['word_id'])

    @Slot(str)
    def openFolder(self, identity):
        if self.documents.available():
            row = next((row for row in self.data.get('rows', []) if row['id'] == identity), {})
            if row.get('word_id'):
                try:
                    job = jobs.read(self.bridge.library.directory, row['word_id'])
                    path = Path(job.get('export_path', ''))
                    if path.is_file():
                        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))
                except (OSError, ValueError) as exc:
                    self._error(str(exc))
