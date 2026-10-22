"""Shared Qt controls for sequential conversion and narration batches."""

import copy
from threading import Event
from time import monotonic

from PySide6.QtCore import Property, QObject, Qt, QTimer, Signal, Slot

from . import batch_jobs


class BatchQueue(QObject):
    changed = Signal()
    progressed = Signal(object)

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.data = {}
        self._running = self._stopping = False
        self._shown = True
        self.cancel = Event()
        self.progressed.connect(self._progress)
        self._progress_timer = QTimer(self)
        self._progress_timer.setSingleShot(True)
        self._progress_timer.setInterval(40)
        self._progress_timer.timeout.connect(self.changed.emit)
        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.setTimerType(Qt.TimerType.PreciseTimer)
        self._clock.timeout.connect(self.changed.emit)
        identity = bridge.library.setting('last_batch_queue', '')
        if identity:
            try:
                saved = batch_jobs.load(bridge.library.directory, identity)
                if saved.get('phase') != 'dismissed':
                    self.data = saved
                    if saved['phase'] == 'running':
                        saved.update(phase='paused', message='Lượt trước chưa hoàn tất. Bấm Tiếp tục; phần đã làm được giữ.')
                        for row in saved['rows']:
                            if row['status'] == 'running':
                                row.update(status='waiting', message='Chờ tiếp tục')
            except (OSError, ValueError, KeyError, TypeError):
                bridge.logger.info('Saved batch is unavailable; original lessons remain in the library.')

    @Property(bool, notify=changed)
    def running(self):
        return self._running

    @Property('QVariantMap', notify=changed)
    def state(self):
        rows = self.data.get('rows', [])
        counts = {status: sum(row['status'] == status for row in rows)
                  for status in ('waiting', 'running', 'done', 'failed')}
        snapshot = copy.deepcopy(self.data)
        complete = bool(rows) and snapshot.get('phase') == 'finished' and counts['done'] == len(rows) and not self._running
        age = max(0, monotonic()-snapshot.get('clock_monotonic', monotonic())) if self._running and snapshot.get('phase') == 'running' else 0
        snapshot['elapsed_seconds'] = snapshot.get('elapsed_seconds', 0)+age
        for row in snapshot.get('rows', []):
            if row['status'] == 'running':
                row['elapsed_seconds'] = row.get('elapsed_seconds', 0)+age
        return {**snapshot, 'running': self._running, 'stopping': self._stopping,
                'shown': self._shown and not complete, 'complete': complete, 'counts': counts, 'total': len(rows),
                'canResume': not self._running and bool(counts['waiting']),
                'canRetry': not self._running and bool(counts['failed'])}

    def available(self):
        bridge = self.bridge
        if (self._running or bridge.busy or bridge.narrationBusy or bridge._browser_running
                or bridge.powerpoint_worker or bridge.classroom.running or bridge.inputDocuments.busy
                or bridge._completed_export_request is not None):
            bridge.inform('Hoàn tất hoặc dừng tác vụ hiện tại trước khi bắt đầu lượt xử lý mới.', True, refresh=False)
            return False
        return True

    @Slot(str, 'QVariantList', result=bool)
    def selectFiles(self, kind, urls):
        if not self.available():
            return False
        if kind == 'convert' and not self.bridge.googleTranslation:
            self.bridge.inform('Chế độ chuyển đổi hiện tại nhận một bài mỗi lượt.', True, refresh=False)
            return False
        try:
            self.data = batch_jobs.selection(kind, list(urls))
            self._shown = True
            self.changed.emit()
            return True
        except ValueError as exc:
            self.bridge.inform(str(exc), True, refresh=False)
            return False

    @Slot(str)
    def remove(self, identity):
        if self._running or self.data.get('phase') != 'draft':
            return
        self.data['rows'] = [row for row in self.data['rows'] if row['id'] != identity]
        if not self.data['rows']:
            self.data = {}
        self.changed.emit()

    @Slot('QVariantList')
    def selectLessons(self, identities):
        if not self.available():
            return
        directory = self.bridge.library.directory

        def ready(value):
            self.data, self._shown = value, True
            self.changed.emit()
            self.bridge.navigate.emit('voice')
            skipped = value.get('skipped_ready', 0)
            if skipped:
                self.bridge.inform(f'Đã chọn {len(value["rows"])} bài chưa có giọng; bỏ qua {skipped} bài đã có giọng hoàn tất.', refresh=False)

        self.bridge.launch(lambda: batch_jobs.library_selection(directory, list(identities)), ready,
                           cancellable=False, message='Đang chuẩn bị các bài đã chọn…')

    @Slot()
    def clear(self):
        if not self.available():
            return

        def completed(_=None):
            self.data = {}
            self.changed.emit()
        if self.data.get('revision'):
            state, directory = copy.deepcopy(self.data), self.bridge.library.directory
            self.bridge.launch(lambda: batch_jobs.dismiss(directory, state), completed,
                               cancellable=False, message='Đang bỏ danh sách; các bài đã tạo được giữ…')
        else:
            completed()

    @Slot()
    def hide(self):
        self._shown = False
        self.changed.emit()

    @Slot()
    def show(self):
        self._shown = True
        self.changed.emit()

    @Slot('QVariantMap')
    def startConversion(self, options):
        if self.data.get('kind') != 'convert' or not self.available():
            return
        if not self.bridge.googleTranslation:
            return
        if self.data.get('phase') == 'draft':
            from .chatgpt_handoff import validate_config
            from .conversion_input import creation_config
            try:
                validate_config(creation_config('Tên theo từng file', options['subject'], options['education'],
                    options['grade'], options['format'], options['preset'], options['style'], options.get('notes', '')))
            except (ValueError, KeyError) as exc:
                self.bridge.inform(str(exc), True, refresh=False)
                return
            self.data['options'] = {**options, 'budget': self.bridge.library.setting('google_character_budget', 500_000),
                                    'bookends': self.bridge.library.setting('template_bookends', False)}
            self.data['summary'] = ('Tiếng Anh' if options['format'] == 'english_only' else 'Song ngữ Việt–Anh') + (
                ' · Giữ thiết kế gốc' if options['style'] == 'source' else ' · Mẫu mới') + (
                f" · {options['subject']} · {options['education']} {options['grade']}")
        self._start()

    @Slot('QVariantMap')
    def startNarration(self, options):
        if self.data.get('kind') != 'voice' or not self.available():
            return
        if self.data.get('phase') == 'draft':
            from .speaker_layout import POSITIONS
            if (options.get('mode') not in {'vi', 'en', 'both'}
                    or not self.bridge._available_voice(options.get('voice', ''))
                    or type(options.get('rate')) is not int or not -3 <= options['rate'] <= 3
                    or options.get('position') not in POSITIONS):
                self.bridge.inform('Chọn ngôn ngữ, giọng, tốc độ và vị trí loa hợp lệ.', True, refresh=False)
                return
            self.data['options'] = dict(options)
            name = next((row['name'] for row in self.bridge.multilingualVoices if row['id'] == options['voice']), 'Giọng đã chọn')
            from . import speech

            self.data['summary'] = {'en': 'Tiếng Anh', 'vi': 'Tiếng Việt', 'both': 'Việt + Anh'}[options['mode']] + (
                f" · {name} · {round(speech._SPEEDS[options['rate']+3]*100)}% · {POSITIONS[options['position']]}")
        self._start()

    @Slot()
    def resume(self):
        if self.data.get('phase') != 'draft' and self.available():
            self._start()

    @Slot()
    def retryFailed(self):
        if self.data.get('phase') != 'draft' and self.available():
            self._start(retry=True)

    def _start(self, retry=False):
        if not self.data.get('rows') or not self.data.get('options'):
            return
        bridge = self.bridge
        bridge.stopSpeech()
        self._running, self._stopping, self._shown = True, False, True
        self.data['clock_monotonic'] = monotonic()
        self._clock.start()
        self.cancel = Event()
        state, directory, cancel = copy.deepcopy(self.data), bridge.library.directory, self.cancel
        self.changed.emit()

        def completed(value):
            self._clock.stop()
            self._progress_timer.stop()
            self.data = value
            self._running = self._stopping = False
            self.changed.emit()
            bridge._catalog.refresh()
            bridge.googleSettings.refresh()
            counts = self.state['counts']
            bridge.inform(f"Hàng đợi: {counts['done']}/{len(value['rows'])} bài hoàn tất"
                          + (f" · {counts['failed']} bài cần thử lại" if counts['failed'] else '')
                          + (f" · {counts['waiting']} bài chờ tiếp tục" if counts['waiting'] else ''),
                          refresh=False)

        bridge.launch(lambda: batch_jobs.run(directory, state, cancel, self.progressed.emit, retry=retry),
                      completed, message='Đang xử lý hàng đợi · mỗi lần một bài…')

    @Slot(object)
    def _progress(self, value):
        if self._running and value.get('id') == self.data.get('id'):
            if value.get('phase') == 'running' and self.data.get('phase') != 'running':
                self._clock.start()
            self.data = value
            if not self._progress_timer.isActive():
                self._progress_timer.start()

    @Slot()
    def stop(self):
        if self._running:
            self.cancel.set()
            self._stopping = True
            self.changed.emit()

    @Slot(str)
    def openResult(self, identity):
        if not self.available():
            return
        row = next((row for row in self.data.get('rows', []) if row['id'] == identity), {})
        if row.get('lesson_id'):
            self.hide()
            if self.data['kind'] == 'voice':
                self.bridge.openLessonNarration(row['lesson_id'])
            else:
                self.bridge.openLesson(row['lesson_id'])

    @Slot(str)
    def openFolder(self, identity):
        from pathlib import Path

        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        row = next((row for row in self.data.get('rows', []) if row['id'] == identity), {})
        if row.get('output') and Path(row['output']).is_file():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(row['output']).parent)))
