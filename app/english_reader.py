"""One cancellable slide queue using existing offline TTS and native WAV playback."""

import ctypes
import shutil
import tempfile
import wave
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from . import speech
from .narration_timing import PARAGRAPH_GAP_MS
from .slide_speech import speech_chunks


class WindowsWavePlayer:
    """MCI supports real playback position; pause does not restart the sentence."""

    def __init__(self):
        self.alias = "bcl_reader_" + str(id(self))
        self.opened = False
        self.playback_directory = None
        self.volume = 100
        self.source = None

    def _command(self, command):
        buffer = ctypes.create_unicode_buffer(512)
        code = ctypes.windll.winmm.mciSendStringW(command, buffer, len(buffer), None)
        if code:
            raise RuntimeError("Không phát được âm thanh. Kiểm tra thiết bị loa của Windows.")
        return buffer.value

    def play(self, path, *, start_ms=0, paused=False):
        self.stop()
        path = str(Path(path).resolve())
        self.source = path
        if '"' in path:
            raise ValueError("Đường dẫn âm thanh không hợp lệ.")
        # MCI rejects some long, hash-named WAV paths even though the WAV is valid.
        # Play an unchanged copy with a short filename; keep the content cache intact.
        self.playback_directory = Path(tempfile.mkdtemp(prefix="bclr-"))
        copy = self.playback_directory / "read.wav"
        if self.volume == 100:
            shutil.copyfile(path, copy)
        else:
            self._attenuate(path, copy, self.volume)
        path = str(copy)
        self._command(f'open "{path}" type waveaudio alias {self.alias}')
        self.opened = True
        self._command(f"set {self.alias} time format milliseconds")
        if paused:
            self._command(f'seek {self.alias} to {int(start_ms)}')
        else:
            self._command(f"play {self.alias}" + (f' from {int(start_ms)}' if start_ms else ''))

    @staticmethod
    def _attenuate(source, destination, volume):
        import numpy as np

        with wave.open(str(source), 'rb') as original:
            if original.getsampwidth() != 2 or original.getcomptype() != 'NONE':
                raise ValueError('Chỉ điều chỉnh âm lượng lời đọc PCM 16 bit đã lưu.')
            samples = np.frombuffer(original.readframes(original.getnframes()), dtype='<i2')
            samples = (samples.astype(np.float32) * (volume / 100)).astype('<i2')
            with wave.open(str(destination), 'wb') as output:
                output.setparams(original.getparams())
                output.writeframes(samples.tobytes())

    def set_volume(self, volume):
        volume = max(0, min(100, int(volume)))
        if volume == self.volume:
            return
        self.volume = volume
        if not self.opened:
            return
        # Attenuate only our private playback copy. Reopen at the same position;
        # never change Windows/device volume or the cached teaching WAV.
        position = int(self._command(f'status {self.alias} position'))
        paused = self._command(f'status {self.alias} mode') == 'paused'
        self.play(self.source, start_ms=position, paused=paused)

    def pause(self):
        if self.opened:
            self._command(f"pause {self.alias}")

    def resume(self):
        if self.opened:
            position = self._command(f"status {self.alias} position")
            self._command(f"play {self.alias} from {int(position)}")

    def finished(self):
        return self.opened and self._command(f"status {self.alias} mode") == "stopped"

    def stop(self):
        if self.opened:
            try:
                self._command(f"close {self.alias}")
            finally:
                self.opened = False
        if self.playback_directory is not None:
            (self.playback_directory / "read.wav").unlink(missing_ok=True)
            self.playback_directory.rmdir()  # Only our named, now-empty folder; no recursive removal.
            self.playback_directory = None


class SpeechJob(QThread):
    def __init__(self, text, voice, rate, directory, generation, parent):
        super().__init__(parent)
        self.arguments = text, voice, rate, directory
        self.generation = generation
        self.value = None

    def run(self):
        try:
            self.value = speech.synthesize(*self.arguments), ""
        except Exception:
            self.value = None, "Chưa tạo được giọng đọc. Kiểm tra giọng trong Cài đặt."


class EnglishReader(QObject):
    changed = Signal()
    failed = Signal(str)
    speakingChanged = Signal(bool)
    chunkFinished = Signal(int)

    def __init__(self, directory, parent=None, player=None):
        super().__init__(parent)
        self.directory = Path(directory)
        self.player = player or WindowsWavePlayer()
        self.state = "stopped"
        self.message = "Đã dừng"
        self.position = 0
        self.queue = []
        self.voice = ""
        self.rate = 0
        self.generation = 0
        self.worker = None
        self._pending = None
        self._result = None
        self._last = None
        self.cache_only = False
        self._between_chunks = False
        self.gap = QTimer(self)
        self.gap.setSingleShot(True)
        self.gap.setInterval(PARAGRAPH_GAP_MS)
        self.gap.timeout.connect(self._finish_gap)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._tick)

    def _state(self, state, message):
        was_speaking = self.state == 'reading'
        self.state, self.message = state, message
        if was_speaking != (state == 'reading'):
            self.speakingChanged.emit(state == "reading")
        self.changed.emit()

    def start(self, texts, voice, rate, *, cache_only=False):
        self.stop()
        self.cache_only = cache_only
        try:
            chunks = [part for text in texts for part in speech_chunks(text)]
        except ValueError as exc:
            self._error(str(exc))
            return
        if not chunks:
            self._state("stopped", "Chưa có nội dung phù hợp để đọc.")
            return
        self.queue, self.voice, self.rate = chunks, voice, rate
        self.position = 0
        self._last = (list(texts), voice, rate)
        self._prepare()

    def _prepare(self):
        if self.position >= len(self.queue):
            self.player.stop()
            self.timer.stop()
            self._state("stopped", "Đã đọc xong phần đang chọn.")
            return
        if self.cache_only:
            path = self.directory / (speech.audio_key(self.queue[self.position], self.voice, self.rate) + '.wav')
            if not speech.valid_audio(path):
                self._error('Giọng đọc đã lưu bị thiếu. Tạo lại giọng trước khi dạy.')
                return
            try:
                self.player.play(path)
                self._state('reading', f'Đang đọc · {self.position+1}/{len(self.queue)}')
                self.timer.start()
            except Exception as exc:
                self._error(str(exc))
            return
        generation = self.generation
        if self.state != "paused":
            self._state("preparing", f"Đang chuẩn bị · {self.position+1}/{len(self.queue)}")
        if self.worker is not None:
            self._pending = generation
            return  # Never run two synthesis workers for repeated clicks.
        self._pending = None
        worker = SpeechJob(self.queue[self.position], self.voice, self.rate, self.directory, generation, self)
        self.worker = worker
        worker.finished.connect(self._worker_finished)
        worker.start()

    @Slot()
    def _worker_finished(self):
        worker = self.sender()
        result, generation = worker.value, worker.generation
        self.worker = None
        worker.deleteLater()
        if self._pending == self.generation:
            self._prepare()
            return
        if generation != self.generation or not self.queue:
            return
        if not result or result[1]:
            self._error(result[1] if result else "Chưa tạo được âm thanh.")
            return
        try:
            self.player.play(result[0]["path"])
            if self.state == "paused":
                self.player.pause()
            else:
                self._state("reading", f"Đang đọc · {self.position+1}/{len(self.queue)}")
            self.timer.start()
        except Exception as exc:
            self._error(str(exc))

    def _error(self, message):
        self.stop()
        self._state("error", message)
        self.failed.emit(message)

    def pause(self):
        if self.state not in {"reading", "preparing"}:
            return
        try:
            self.player.pause()
            self._state("paused", "Tạm dừng")
        except Exception as exc:
            self._error(str(exc))

    def resume(self):
        if self.state != "paused":
            return
        try:
            if self._between_chunks:
                self._state('reading', 'Đang đọc')
                self.gap.start()
            elif self.worker is not None:
                self._state("preparing", "Đang chuẩn bị")
            else:
                self.player.resume()
                self._state("reading", "Đang đọc")
        except Exception as exc:
            self._error(str(exc))

    def stop(self):
        self.generation += 1
        self._pending = None
        self.queue = []
        self.timer.stop()
        self.gap.stop()
        self._between_chunks = False
        try:
            self.player.stop()
        except Exception:
            pass
        self._state("stopped", "Đã dừng")

    def _tick(self):
        if self.state != "reading":
            return
        try:
            if self.player.finished():
                self.player.stop()
                self.timer.stop()
                self.position += 1
                self.chunkFinished.emit(self.position - 1)
                if self.position < len(self.queue):
                    self._between_chunks = True
                    self.gap.start()
                else:
                    self._prepare()
        except Exception as exc:
            self._error(str(exc))

    def _finish_gap(self):
        if self.state == 'reading' and self._between_chunks:
            self._between_chunks = False
            self._prepare()

    def shutdown(self):
        self.stop()
        if self.worker is not None:
            self.worker.wait()  # CPU inference cannot be safely terminated mid-engine call.

    def summary(self):
        return {"state": self.state, "message": self.message,
                "position": self.position+1 if self.queue else 0, "total": len(self.queue)}
