"""Isolated settings requests: no lesson/UI refresh and no GUI-thread database wait."""

import json
import sqlite3
import time
from contextlib import closing
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal, Slot


def store_preference(directory, values):
    with closing(sqlite3.connect(Path(directory) / 'library.db', timeout=2)) as database:
        with database:
            database.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                             ('voice_options', json.dumps(values, ensure_ascii=False)))
    return values


class VoiceTask(QThread):
    def __init__(self, action, parent):
        super().__init__(parent)
        self.action = action
        self.value, self.error = None, ''
        self.cancel = Event()
        self.generation = 0
        self.started_at = time.monotonic()

    def run(self):
        try:
            self.value = self.action(self.cancel)
        except InterruptedError:
            pass
        except Exception as exc:
            self.error = str(exc)


class VoiceControls(QObject):
    changed = Signal()
    saved = Signal()
    ready = Signal(object)
    failed = Signal(str)

    def __init__(self, directory, parent=None):
        super().__init__(parent)
        self.directory = Path(directory)
        self.save_worker = None
        self.pending_save = None
        self.preview_workers = []
        self.generation = 0
        self.pending = None
        self.phase = 'idle'
        self.kind = ''
        self.message = ''
        self.save_message = ''
        self.save_error = False
        self.preview_seconds = 0
        self.save_seconds = 0

    def summary(self):
        return {'saving': self.save_worker is not None, 'saveMessage': self.save_message,
                'saveError': self.save_error, 'phase': self.phase, 'message': self.message,
                'previewSeconds': self.preview_seconds, 'saveSeconds': self.save_seconds, 'kind': self.kind}

    def save(self, voice, rate, en_rate=None):
        self.pending_save = {'voice': voice, 'rate': rate}
        if en_rate is not None:
            self.pending_save.update(vi_rate=rate, en_rate=en_rate)
        if self.save_worker is not None:
            return
        self._start_save()

    def _start_save(self):
        values, self.pending_save = self.pending_save, None
        task = VoiceTask(lambda _: store_preference(self.directory, values), self)
        self.save_worker = task
        self.save_message, self.save_error = 'Đang lưu giọng và tốc độ…', False
        task.finished.connect(self._saved)
        self.changed.emit()
        task.start()

    @Slot()
    def _saved(self):
        task, self.save_worker = self.save_worker, None
        task.wait()  # finished can precede the last native thread cleanup.
        if self.pending_save is not None:
            task.deleteLater()
            self._start_save()
            return
        self.save_seconds = time.monotonic() - task.started_at
        self.save_error = bool(task.error)
        self.save_message = ('Chưa lưu được giọng. Thư viện đang bận hoặc không ghi được; thử lưu lại.'
                             if task.error else 'Đã lưu cặp giọng Việt–Mỹ cho lần tạo mới. Bài đã tạo giữ nguyên.')
        self.changed.emit()
        if task.error:
            self.failed.emit(self.save_message)
        else:
            self.saved.emit()
        task.deleteLater()

    def preview(self, text, voice, rate, *, kind='pair', en_rate=None):
        self.stop()
        self.kind = kind
        self.phase, self.message = 'preparing', 'Đang chuẩn bị câu nghe thử…'
        request = self.generation, text, voice, rate, en_rate
        self.changed.emit()
        if len(self.preview_workers) >= 2:
            self.pending = request  # Only the latest request survives rapid clicks.
        else:
            self._start_preview(request)

    def _start_preview(self, request):
        from .voice_preview import preview

        generation, text, voice, rate, en_rate = request
        arguments = {} if en_rate is None else dict(en_rate=en_rate)
        task = VoiceTask(lambda cancel: preview(text, voice, rate, self.directory / 'audio', cancel=cancel, **arguments), self)
        task.generation = generation
        task.finished.connect(self._preview_finished)
        self.preview_workers.append(task)
        task.start()

    @Slot()
    def _preview_finished(self):
        from .voice_errors import public_message

        task = self.sender()
        task.wait()
        self.preview_workers.remove(task)
        if task.generation == self.generation and not task.cancel.is_set():
            self.preview_seconds = time.monotonic() - task.started_at
            self.phase = 'error' if task.error or not task.value else 'playing'
            self.message = public_message(task.error) or ('Đang nghe thử · cấu hình chỉ đổi khi bấm Lưu.' if task.value else 'Đã dừng nghe thử.')
            self.changed.emit()
            if task.error:
                self.failed.emit(self.message)
            elif task.value:
                self.ready.emit(task.value)
        task.deleteLater()
        if self.pending is not None:
            request, self.pending = self.pending, None
            if request[0] == self.generation:
                self._start_preview(request)

    def stop(self):
        self.generation += 1
        self.pending = None
        for task in self.preview_workers:
            task.cancel.set()
        self.phase, self.message = 'idle', ''
        self.kind = ''
        self.changed.emit()

    def shutdown(self):
        self.stop()
        for task in list(self.preview_workers):
            task.wait()
        if self.save_worker is not None:
            self.save_worker.wait()
        if self.pending_save is not None:
            values, self.pending_save = self.pending_save, None
            try:
                store_preference(self.directory, values)
            except (sqlite3.Error, OSError) as exc:
                self.failed.emit('Chưa lưu được cặp giọng gần nhất: ' + str(exc))
