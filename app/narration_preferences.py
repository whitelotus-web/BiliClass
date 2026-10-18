"""Remember the last deliberate language choice without blocking Qt on SQLite."""

import json
import sqlite3
from contextlib import closing

from PySide6.QtCore import Property, QObject, Signal, Slot

from .voice_controls import VoiceTask

MODES = {'vi', 'en', 'both'}


def read_mode(library):
    saved = library.setting('narration_last_mode', 'en')
    return saved if isinstance(saved, str) and saved in MODES else 'en'


def store_mode(directory, mode):
    if mode not in MODES:
        raise ValueError('Chọn tiếng Việt, tiếng Anh hoặc Việt + Anh.')
    with closing(sqlite3.connect(directory / 'library.db', timeout=2)) as db, db:
        db.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                   ('narration_last_mode', json.dumps(mode)))


class NarrationPreferences(QObject):
    changed = Signal()
    failed = Signal(str)

    def __init__(self, library, parent=None):
        super().__init__(parent)
        self.directory, self._mode = library.directory, read_mode(library)
        self.worker = None
        self.pending = None

    @Property(str, notify=changed)
    def mode(self):
        return self._mode

    @Slot(str)
    def select(self, mode):
        if mode not in MODES:
            return
        self._mode = self.pending = mode
        self.changed.emit()
        self._start()

    def _start(self):
        if self.worker is not None or self.pending is None:
            return
        mode, self.pending = self.pending, None
        self.worker = VoiceTask(lambda _: store_mode(self.directory, mode), self)
        self.worker.finished.connect(self._finished)
        self.worker.start()

    @Slot()
    def _finished(self):
        worker, self.worker = self.worker, None
        if worker.error:
            self.failed.emit('Chưa lưu được chế độ giọng gần nhất: ' + worker.error)
        worker.deleteLater()
        self._start()

    def shutdown(self):
        if self.worker:
            self.worker.wait()
        if self.pending:
            try:
                store_mode(self.directory, self.pending)
                self.pending = None
            except (sqlite3.Error, OSError) as exc:
                self.failed.emit('Chưa lưu được chế độ giọng gần nhất: ' + str(exc))
