"""Responsive Google controls; all key, disk and model checks run off Qt's thread."""

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from .google_settings_tasks import change, read_state
from .google_translation import DEFAULT_BUDGET
from .jobs import Job


class GoogleSettings(QObject):
    changed = Signal()
    saved = Signal(bool)

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge, self.directory = bridge, bridge.library.directory
        self._state = dict(keys=[], budget=DEFAULT_BUDGET, configured=False, message='',
                           ocrReady=False, powerpointInstalled=False, health={})
        from .translation_health import summarize

        self._state['health'] = summarize([], DEFAULT_BUDGET)
        self.worker = None
        self._result = None
        self._pending = self._closed = self._mutating = False
        self._generation = 0
        self._ready = False
        self._timer = QTimer(self)
        self._timer.setInterval(30_000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        bridge.destroyed.connect(self.shutdown)
        QTimer.singleShot(0, self.refresh)

    @Property('QVariantMap', notify=changed)
    def state(self):
        return self._state

    @Property(bool, notify=changed)
    def loading(self):
        return self.worker is not None or self._mutating

    @Property(bool, notify=changed)
    def ready(self):
        return self._ready

    @Slot()
    def refresh(self):
        if self._closed:
            return
        if self.worker is not None or self._mutating:
            self._pending = True
            return
        self._pending = False
        self._result = None
        self.worker = Job(lambda: read_state(self.directory), self)
        self.worker.generation = self._generation
        self.worker.completed.connect(self._received)
        self.worker.finished.connect(self._finished)
        self.worker.start()
        self.changed.emit()

    @Slot(object, str)
    def _received(self, result, error):
        self._result = result, error

    @Slot()
    def _finished(self):
        task = self.sender()
        if task is None or task is not self.worker:
            return
        self.worker = None
        if not self._closed and not self._mutating and task.generation == self._generation:
            self._ready = True
            result, error = self._result
            if error:
                # A transient disk/SQLite failure must not erase the last known keys.
                self._state = {**self._state, 'message': error}
            else:
                self._state = result
        task.deleteLater()
        self.changed.emit()
        pending, self._pending = self._pending, False
        if pending and not self._closed and not self._mutating:
            self.refresh()

    def _operate(self, operation, values, message, *, saving=False):
        if self._closed or self.bridge._busy or self._mutating:
            return False
        self._generation += 1
        self._mutating = True

        def finished(result):
            self._mutating = False
            success = not result['error']
            if success:
                self._state = result['state']
                self._ready = True
            self.changed.emit()
            if saving:
                self.saved.emit(success)
            self.bridge.inform(message if success else result['error'], not success, refresh=False)

        self.bridge.launch(lambda: change(self.directory, operation, values), finished,
                           cancellable=False, message='Đang lưu cấu hình Google Dịch…')
        self.changed.emit()
        return True

    @Slot(str, str)
    def rename(self, key_id, name):
        self._operate('rename', (key_id, name), 'Đã đổi tên key. Bộ đếm riêng được giữ nguyên.')

    @Slot(str, int, result=bool)
    def save(self, text, budget):
        if not 1 <= budget <= DEFAULT_BUDGET:
            self.bridge.inform('Giới hạn cục bộ từ 1 đến 500.000 ký tự/key/tháng.', True, refresh=False)
            return False
        return self._operate('save', (text, budget),
            'Đã lưu cấu hình Google Dịch. Key được mã hóa trên tài khoản Windows này.', saving=True)

    @Slot(str)
    def remove(self, key_id):
        self._operate('remove', (key_id,), 'Đã xóa key đã chọn.')

    @Slot()
    def recheck(self):
        self._operate('recheck', (), 'Đã cho phép thử lại key ở lượt dịch tiếp theo. Bộ đếm ký tự được giữ nguyên.')

    @Slot()
    def prepareOcr(self):
        if self.bridge._busy:
            return
        from .local_ocr import model_paths, prepare_models
        from .vietnamese_ocr import pack_directory

        def work():
            prepare_models()
            return bool(model_paths() and pack_directory())

        def done(ready):
            self._state = {**self._state, 'ocrReady': ready}
            self.refresh()
            self.bridge.inform('Đã chuẩn bị nhận diện chữ Việt–Anh trong ảnh.' if ready else
                'Đã có OCR cơ bản. Cần gói OCR Việt–Anh đầy đủ để kiểm tra dấu trước khi tự che chữ trong ảnh.')

        self.bridge.launch(work, done)

    @Slot()
    def shutdown(self):
        if self._closed:
            return
        self._closed = True
        self._timer.stop()
        if self.worker is not None:
            task, self.worker = self.worker, None
            task.wait()
            task.deleteLater()
