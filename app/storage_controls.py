"""Qt controls for verified relocation, followed by a clean application restart."""

from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication


class StorageControls(QObject):
    changed = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self._moving = False
        self.transfer_record = None
        self.next_directory = None

    @Property(bool, notify=changed)
    def moving(self):
        return self._moving

    def available(self):
        b = self.bridge
        backup = getattr(b, '_automatic_backup', None)
        cleanup = getattr(b, '_storage_cleanup', None)
        return not (b.busy or b.narrationBusy or b.powerpoint_worker or b.classroom.running
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
