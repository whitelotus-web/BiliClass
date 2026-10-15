"""Conversion milestones, not an invented percentage of ChatGPT's generation."""

import json
import time
from contextlib import contextmanager, nullcontext
from pathlib import Path

STAGES = {
    "session": (2, 5, "Mở phiên ChatGPT"),
    "model": (5, 8, "Chọn model và suy luận"),
    "upload": (8, 25, "Tải tài liệu và gửi yêu cầu"),
    "waiting": (25, 25, "Chờ ChatGPT tạo PowerPoint"),
    "translate": (25, 55, "Biên soạn từng phần bài giảng"),
    "assemble": (55, 60, "Hoàn thiện PowerPoint tại máy"),
    "download": (55, 60, "Nhận PowerPoint"),
    "quality": (60, 72, "Kiểm tra slide và lời đọc"),
    "refine": (73, 75, "Gửi yêu cầu sửa slide"),
    "refine_wait": (75, 75, "Chờ ChatGPT sửa PowerPoint"),
    "refine_download": (78, 80, "Nhận bản sửa"),
    "refine_quality": (80, 86, "Kiểm tra bản sửa"),
    "import": (86, 88, "Nhập bài vào thư viện"),
    "audio": (88, 97, "Chuẩn bị giọng đọc Việt–Anh"),
    "save": (98, 99, "Lưu bài giảng"),
    "completed": (100, 100, "Đã nhận và lưu bài giảng"),
}


def emit_progress(progress, stage, message, done=None, total=None):
    """Keep existing string callbacks compatible with structured progress sinks."""
    if progress is None:
        return
    if hasattr(progress, "stage"):
        progress.stage(stage, message, done, total)
    else:
        progress(message)


def scoped_progress(progress, stage):
    return progress.scope(stage) if hasattr(progress, "scope") else progress


def measured(progress, operation):
    """Private timings, without document text or browser credentials."""
    return progress.measure(operation) if hasattr(progress, "measure") else nullcontext()


class ConversionProgress:
    def __init__(self, folder, notify):
        self.path = Path(folder) / "conversion-progress.json"
        self.notify = notify
        self.started = time.monotonic()
        self.state = {"percent": 0, "stage": "session", "stageLabel": STAGES["session"][2],
                      "done": 0, "total": 0, "waiting": False, "elapsedSeconds": 0}
        previous = {}
        try:
            previous = json.loads(self.path.read_text(encoding="utf-8"))
            if (isinstance(previous, dict) and previous.get("version") == 1 and previous.get("stage") in STAGES
                    and type(previous.get("percent")) is int and 0 <= previous["percent"] <= 100
                    and type(previous.get("elapsedSeconds")) is int and previous["elapsedSeconds"] >= 0):
                self.state.update({k: previous[k] for k in self.state if k in previous})
                # Only the main-thread library commit may mark this run complete.
                self.state["percent"] = min(self.state["percent"], 99)
        except (OSError, ValueError, TypeError):
            pass
        self.elapsed = self.state["elapsedSeconds"]
        self.ended = None
        self.persisted = None
        self.last_saved = None
        self.stage_started = time.monotonic()
        durations = previous.get('stageSeconds', {}) if isinstance(previous, dict) else {}
        self.stage_seconds = {key: value for key, value in durations.items()
                              if key in STAGES and type(value) in (int, float) and 0 <= value < 10**9} if isinstance(durations, dict) else {}
        operations = previous.get('operations', {}) if isinstance(previous, dict) else {}
        self.operations = {key: dict(value) for key, value in operations.items()
                           if isinstance(key, str) and key.startswith('local.') and isinstance(value, dict)
                           and set(value) == {'calls', 'seconds', 'failures'}
                           and all(type(v) in (int, float) and 0 <= v < 10**9 for v in value.values())} if isinstance(operations, dict) else {}

    @contextmanager
    def measure(self, operation):
        started = time.monotonic()
        failed = False
        try:
            yield
        except BaseException:
            failed = True
            raise
        finally:
            row = self.operations.setdefault(operation, {"calls": 0, "seconds": 0, "failures": 0})
            row["calls"] += 1
            row["seconds"] = round(row["seconds"] + time.monotonic() - started, 4)
            row["failures"] += int(failed)
            self._emit(force=True)

    def __call__(self, message):
        self.state["message"] = message
        self._emit()

    def stage(self, stage, message, done=None, total=None):
        if stage != self.state["stage"]:
            previous = self.state["stage"]
            self.stage_seconds[previous] = self.stage_seconds.get(previous, 0) + time.monotonic() - self.stage_started
            self.stage_started = time.monotonic()
        start, end, label = STAGES[stage]
        counted = type(total) is int and total > 0 and type(done) is int
        done = min(total, max(0, done)) if counted else 0
        percent = start + int((end-start)*done/total) if counted else start
        self.state.update(percent=max(self.state["percent"], percent), stage=stage, stageLabel=label,
                          done=done, total=total if counted else 0,
                          waiting=stage in {"waiting", "refine_wait", "translate"}, message=message)
        self._emit()

    def finish(self):
        if self.ended is None:
            self.ended = time.monotonic()
        self._emit(force=True)

    def _emit(self, force=False):
        self.state["elapsedSeconds"] = self.elapsed + int((self.ended if self.ended is not None else time.monotonic())-self.started)
        self.notify({**self.state, "emittedAtMs": int(time.time()*1000)})
        checkpoint = (self.state["stage"], self.state["percent"])
        if not force and self.persisted == checkpoint and self.last_saved is not None and time.monotonic() - self.last_saved < 5:
            return
        durations = {**self.stage_seconds}
        current = self.state["stage"]
        durations[current] = durations.get(current, 0) + (self.ended if self.ended is not None else time.monotonic()) - self.stage_started
        saved = {"version": 1, **self.state, "stageSeconds": {k: round(v, 2) for k, v in durations.items()},
                 "operations": self.operations}
        try:
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
            temporary.replace(self.path)
            self.persisted = checkpoint
            self.last_saved = time.monotonic()
        except OSError:
            # Progress persistence must never cause a repeat of a web submission.
            pass

    def scope(self, stage):
        owner = self

        class Scoped:
            def __call__(self, message):
                owner(message)

            def stage(self, ignored, message, done=None, total=None):
                owner.stage(stage, message, done, total)

        return Scoped()
