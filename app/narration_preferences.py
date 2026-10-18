"""Remember the last deliberate language choice without blocking Qt on SQLite."""

import json
import sqlite3
from contextlib import closing

from PySide6.QtCore import Property, QObject, Signal, Slot

from .speaker_layout import position as speaker_position
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


def store_choices(directory, choices):
    with closing(sqlite3.connect(directory / 'library.db', timeout=2)) as db, db:
        for key, value in choices.items():
            db.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                       (key, json.dumps(value)))


def store_lesson_position(directory, lesson_id, selected):
    from .speaker_layout import POSITIONS

    if selected not in POSITIONS:
        raise ValueError('Chọn vị trí loa hợp lệ.')
    with closing(sqlite3.connect(directory / 'library.db', timeout=2)) as db, db:
        if not db.execute("UPDATE lessons SET content=json_set(content, '$.speaker_position', ?) WHERE id=?",
                          (selected, lesson_id)).rowcount:
            raise ValueError('Không còn bài giảng để lưu vị trí loa.')
        return json.loads(db.execute('SELECT content FROM lessons WHERE id=?', (lesson_id,)).fetchone()[0])


class NarrationPreferences(QObject):
    changed = Signal()
    failed = Signal(str)

    def __init__(self, library, parent=None):
        super().__init__(parent)
        self.directory, self._mode = library.directory, read_mode(library)
        self._position = speaker_position(library.setting('narration_speaker_position', 'bottom_right'))
        self.worker = None
        self.pending = {}

    @Property(str, notify=changed)
    def mode(self):
        return self._mode

    @Slot(str)
    def select(self, mode):
        if mode not in MODES:
            return
        self._mode = mode
        self.pending['narration_last_mode'] = mode
        self.changed.emit()
        self._start()

    @Property(str, notify=changed)
    def position(self):
        return self._position

    @Slot(str)
    def selectPosition(self, selected):
        from .speaker_layout import POSITIONS

        if selected not in POSITIONS:
            return
        self._position = selected
        self.pending['narration_speaker_position'] = selected
        self.changed.emit()
        self._start()

    def _start(self):
        if self.worker is not None or not self.pending:
            return
        choices, self.pending = self.pending, {}
        self.worker = VoiceTask(lambda _: store_choices(self.directory, choices), self)
        self.worker.finished.connect(self._finished)
        self.worker.start()

    @Slot()
    def _finished(self):
        worker, self.worker = self.worker, None
        if worker.error:
            self.failed.emit('Chưa lưu được cấu hình giọng gần nhất: ' + worker.error)
        worker.deleteLater()
        self._start()

    def shutdown(self):
        if self.worker:
            self.worker.wait()
        if self.pending:
            try:
                store_choices(self.directory, self.pending)
                self.pending = {}
            except (sqlite3.Error, OSError) as exc:
                self.failed.emit('Chưa lưu được cấu hình giọng gần nhất: ' + str(exc))
