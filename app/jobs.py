"""Qt worker with consistent storage errors."""
from PySide6.QtCore import QThread, Signal


class Job(QThread):
    completed = Signal(object, str)

    def __init__(self, action, parent):
        super().__init__(parent)
        self.action = action
        self.error_code = None

    def run(self):
        try:
            self.completed.emit(self.action(), "")
        except Exception as exc:
            from .storage_space import FULL_DISK_MESSAGE, full_disk_error

            self.error_code = "storage" if full_disk_error(exc) else getattr(exc, "code", None)
            self.completed.emit(None, FULL_DISK_MESSAGE if full_disk_error(exc) else str(exc))
