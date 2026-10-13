"""Conversion milestones, not an invented percentage of ChatGPT's generation."""

import json
import time
from pathlib import Path

STAGES = {
    "session": (2, 5, "Mở phiên ChatGPT"),
    "model": (5, 8, "Chọn model và suy luận"),
    "upload": (8, 25, "Tải tài liệu và gửi yêu cầu"),
    "waiting": (25, 25, "Chờ ChatGPT tạo PowerPoint"),
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


class ConversionProgress:
    def __init__(self, folder, notify):
        self.path = Path(folder) / "conversion-progress.json"
        self.notify = notify
        self.started = time.monotonic()
        self.state = {"percent": 0, "stage": "session", "stageLabel": STAGES["session"][2],
                      "done": 0, "total": 0, "waiting": False, "elapsedSeconds": 0}
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
        self.persisted = None
        self.stage_started = time.monotonic()
        self.stage_seconds = {}

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
                          waiting=stage in {"waiting", "refine_wait"}, message=message)
        self._emit()

    def _emit(self):
        self.state["elapsedSeconds"] = self.elapsed + int(time.monotonic()-self.started)
        self.notify({**self.state, "emittedAtMs": int(time.time()*1000)})
        checkpoint = (self.state["stage"], self.state["percent"])
        if self.persisted == checkpoint:
            return
        durations = {**self.stage_seconds}
        current = self.state["stage"]
        durations[current] = durations.get(current, 0) + time.monotonic() - self.stage_started
        saved = {"version": 1, **self.state, "stageSeconds": {k: round(v, 2) for k, v in durations.items()}}
        try:
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(saved, ensure_ascii=False), encoding="utf-8")
            temporary.replace(self.path)
            self.persisted = checkpoint
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
