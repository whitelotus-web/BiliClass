"""Qt controls for verified relocation, followed by a clean application restart."""

import shutil
from pathlib import Path

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication


class StorageControls(QObject):
    changed = Signal()
    progress = Signal(int, int)

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self._moving = False
        self.transfer_record = None
        self.next_directory = None
        self._backing = False
        self._state = {}
        self.progress.connect(self._progress)
        QTimer.singleShot(0, self.refresh)

    @Property('QVariantMap', notify=changed)
    def state(self):
        return dict(self._state, running=self._backing)

    @Slot()
    def refresh(self):
        from .storage import BACKUP_SCOPE, backup_state

        self._state = dict(backup_state(self.bridge.library.directory), scope=BACKUP_SCOPE)
        try:
            self._state['free_bytes'] = shutil.disk_usage(self.bridge.library.directory).free
        except OSError:
            self._state['free_bytes'] = -1
        self.changed.emit()

    @Slot(int, int)
    def _progress(self, done, total):
        self._state.update(done=done, total=total)
        self.changed.emit()

    def begin_backup(self):
        self._backing = True
        self._state.update(done=0, total=0)
        self.changed.emit()

    def backup(self, destination=None, *, daily=False):
        from .storage import backup_library

        return backup_library(self.bridge.library.directory, destination, daily,
                              progress=lambda done, total: self.progress.emit(done, total))

    def finish_backup(self, path=None, error=''):
        self._backing = False
        self.refresh()
        if error:
            self.bridge.logger.warning('Backup failed: %s', error)
            self.bridge.inform('Chưa sao lưu được: ' + error + ' Xem Cài đặt → Dữ liệu.', True, refresh=False)
        elif path:
            self.bridge.logger.info('Library backup finished')

    @Property(bool, notify=changed)
    def moving(self):
        return self._moving

    def available(self):
        b = self.bridge
        backup = getattr(b, '_automatic_backup', None)
        cleanup = getattr(b, '_storage_cleanup', None)
        return not (b.busy or b.narrationBusy or b.powerpoint_worker or b.classroom.running
                    or getattr(getattr(b, '_google_settings', None), 'loading', False)
                    or b.classroom.busy or b._speaking or b._browser_ai.loginBusy
                    or b.english_reader.worker
                    or b.voice_controls.save_worker or b.voice_controls.preview_workers
                    or b.updateState.get('downloading') or backup and backup.isRunning()
                    or cleanup and cleanup.isRunning())

    @Slot(str, result=str)
    def destination(self, folder_url):
        folder = QUrl(folder_url).toLocalFile()
        return str(Path(folder) / 'BiliClass-Data') if folder else ''

    @Slot(str)
    def relocate(self, folder_url):
        from .library_location import transfer

        if not self.available():
            self.bridge.inform('Hoàn tất tác vụ, đọc thử, trình chiếu và lớp học trước khi chuyển thư viện.', True)
            return
        target = self.destination(folder_url)
        if not target:
            return
        self._moving = True
        self.changed.emit()
        self.bridge._google_settings._timer.stop()

        def finished(record):
            self.transfer_record = record
            self.next_directory = record['target']
            QGuiApplication.quit()

        self.bridge.launch(lambda: transfer(self.bridge.library.directory, target), finished)

    def failed(self):
        automatic = getattr(self.bridge, '_automatic_backup', None)
        if self._backing and not (automatic and automatic.isRunning()):
            self._backing = False
            self.refresh()
        if self._moving and not self.transfer_record:
            self._moving = False
            self.changed.emit()
            self.bridge._google_settings._timer.start()

    @Slot(str)
    def openExisting(self, folder_url):
        if not self.available():
            self.bridge.inform('Hoàn tất tác vụ và lớp học trước khi đổi thư viện.', True)
            return
        path = Path(QUrl(folder_url).toLocalFile())
        if not (path / 'library.db').is_file():
            self.bridge.inform('Thư mục chưa có thư viện BiliClass.', True)
            return
        self.next_directory = str(path.resolve())
        QGuiApplication.quit()
