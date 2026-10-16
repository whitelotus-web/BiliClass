"""Prepare narration after saving the lesson, outside the conversion worker."""

import json
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from threading import Event
from time import monotonic

from PySide6.QtCore import Property, QObject, QThread, QTimer, Signal, Slot

from . import speech
from .browser_audio import narration_tasks


class NarrationJob(QThread):
    progressed = Signal(object)

    def __init__(self, inspection, voices, directory, parent):
        super().__init__(parent)
        self.inspection, self.voices = inspection, dict(voices)
        self.rate, self.directory = voices["rate"], directory
        self.tasks = []
        self.total = self.skipped = self.duplicates = self.initial_cached = 0
        self.parallelism = 1
        self.cancel, self.paused = Event(), Event()
        self.result = {}

    def prepare(self):
        self.tasks, self.skipped, self.duplicates = narration_tasks(self.inspection, self.voices)
        self.total = len(self.tasks)
        missing = []
        for text, voice in self.tasks:
            if self.cancel.is_set():
                raise InterruptedError()
            if not speech.valid_audio(Path(self.directory) / (speech.audio_key(text, voice, self.rate) + '.wav')):
                missing.append((text, voice))
        self.initial_cached = self.total - len(missing)
        self.tasks = missing
        self.parallelism = speech.narration_workers(missing)

    def run(self):
        try:
            self.prepare()
        except InterruptedError:
            self.result = {'complete': 0, 'cached': 0, 'total': self.total, 'failed': 0,
                           'skipped': self.skipped, 'duplicates': self.duplicates, 'cancelled': True}
            return
        except Exception:
            self.result = {'complete': 0, 'cached': 0, 'total': self.total, 'failed': 1,
                           'skipped': self.skipped, 'duplicates': self.duplicates, 'cancelled': False}
            return
        complete = cached = self.initial_cached
        failed = consecutive = 0
        tasks=deque(self.tasks)
        futures={}
        second_enabled=False
        self.progressed.emit({'complete': complete, 'cached': cached, 'total': self.total,
                              'skipped': self.skipped, 'duplicates': self.duplicates,
                              'message': 'Đang tạo giọng đọc trên máy…'})
        try:
            with ThreadPoolExecutor(max_workers=self.parallelism,thread_name_prefix='bcl-narration') as pool:
                stopping=False
                while tasks or futures:
                    if self.cancel.is_set():
                        stopping=True
                    if not stopping and not self.paused.is_set():
                        busy={slot for slot,_ in futures.values()}
                        slots=range(2 if second_enabled else 1)
                        for slot in slots:
                            if slot not in busy and tasks:
                                task=tasks.popleft()
                                function=speech.synthesize_secondary if slot else speech.synthesize_background
                                future=pool.submit(function,*task,self.rate,self.directory,self.cancel)
                                futures[future]=slot,task
                    if not futures:
                        if stopping or not tasks:
                            break
                        self.cancel.wait(.1)
                        continue
                    finished,_=wait(futures,timeout=.1,return_when=FIRST_COMPLETED)
                    for future in finished:
                        slot,task=futures.pop(future)
                        try:
                            result=future.result()
                            complete+=1
                            cached+=bool(result.get('cached'))
                            consecutive=0
                            if not slot and self.parallelism==2:
                                second_enabled=True
                        except InterruptedError:
                            stopping=True
                        except Exception:
                            if slot:
                                # Low RAM/secondary initialization must not lose a line.
                                tasks.appendleft(task)
                                self.parallelism=1
                                second_enabled=False
                            else:
                                failed+=1
                                consecutive+=1
                        self.result={'complete':complete,'cached':cached,'failed':failed,
                                     'total':self.total,'skipped':self.skipped,
                                     'duplicates':self.duplicates,'workers':2 if second_enabled else 1}
                        self.progressed.emit(dict(self.result))
                        if consecutive>=3:
                            stopping=True
                    if stopping and not futures:
                        break
        finally:
            speech._secondary_vieneu_engine.cache_clear()
            self.result = {"complete": complete, "cached": cached, "failed": failed,
                           "total": self.total, "skipped": self.skipped,
                           "duplicates": self.duplicates, "cancelled": self.cancel.is_set(),
                           "workers": self.parallelism}


class NarrationPreparation(QObject):
    changed = Signal()
    clockChanged = Signal()

    def __init__(self, directory, parent):
        super().__init__(parent)
        self.directory = directory
        self.worker = None
        self.pending = None
        self.state = {}
        self.path = None
        self.paused = False
        self.last_checkpoint = 0
        self._started_at = None
        self._elapsed = 0
        self.clock = QTimer(self)
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self.clockChanged)

    @Property(int, notify=clockChanged)
    def elapsedSeconds(self):
        return self._elapsed + (int(monotonic() - self._started_at) if self._started_at is not None else 0)

    def start(self, lesson_id, inspection, voices, folder, metadata=None):
        request = lesson_id, inspection, dict(voices), folder, metadata
        if self.worker is not None:
            self.pending = request
            self.worker.cancel.set()
            return
        self.path = Path(folder) / "narration-progress.json"
        self._elapsed = 0
        self._started_at = monotonic()
        self.worker = NarrationJob(inspection, voices, self.directory, self)
        self.worker.paused.set() if self.paused else self.worker.paused.clear()
        self.state = {**(metadata or {}), "lesson_id": lesson_id, "running": True,
                      "complete": self.worker.initial_cached, "cached": self.worker.initial_cached, "failed": 0,
                      "voice": voices.get("voice", ""), "rate": voices["rate"],
                      "total": self.worker.total, "skipped": self.worker.skipped,
                      "duplicates": self.worker.duplicates, "cancelled": False,
                      "message": "Đang kiểm tra các đoạn giọng đã lưu…"}
        self.worker.progressed.connect(self._progress)
        self.worker.finished.connect(self._finished)
        self._persist()
        self.changed.emit()
        self.clockChanged.emit()
        self.clock.start()
        self.worker.start()

    def pause(self, paused):
        self.paused = bool(paused)
        if self.worker is not None:
            self.worker.paused.set() if paused else self.worker.paused.clear()

    @Slot(object)
    def _progress(self, result):
        if self.sender() is not self.worker:
            return
        self.state.update(result)
        if monotonic() - self.last_checkpoint >= 1:
            self._persist()
        self.changed.emit()

    @Slot()
    def _finished(self):
        worker = self.sender()
        if worker is not self.worker:
            return
        self.state.update(worker.result, running=False)
        self._stop_clock()
        self.state["message"] = self._completion_message(self.state)
        self.worker = None
        self._persist()
        self.changed.emit()
        worker.wait()
        worker.deleteLater()
        if self.pending is not None:
            request, self.pending = self.pending, None
            self.start(*request)

    def _persist(self):
        try:
            self.state['elapsed_seconds'] = self.elapsedSeconds
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps({"version": 1, **self.state}, ensure_ascii=False), encoding="utf-8")
            temporary.replace(self.path)
            self.last_checkpoint = monotonic()
        except OSError:
            pass  # An optional cache checkpoint cannot invalidate a saved lesson.

    @staticmethod
    def _completion_message(result):
        if result.get("cancelled"):
            return "Đã dừng tạo giọng. Các đoạn đã tạo được giữ lại để tiếp tục."
        if result.get("failed") or result.get("skipped"):
            return "Một số lời đọc cần kiểm tra. Bài giảng đã được lưu."
        if not result.get("total"):
            return "Chưa có nội dung phù hợp để tạo giọng đọc."
        return "Giọng đọc sẵn sàng."

    def cancel(self):
        self.pending = None
        if self.worker is not None:
            self.worker.cancel.set()

    def _stop_clock(self):
        self._elapsed = self.elapsedSeconds
        self._started_at = None
        self.clock.stop()
        self.state['elapsed_seconds'] = self._elapsed
        self.clockChanged.emit()

    def shutdown(self):
        self.cancel()
        if self.worker is not None:
            self.worker.wait()  # Finish the current CPU call; never terminate the model.
