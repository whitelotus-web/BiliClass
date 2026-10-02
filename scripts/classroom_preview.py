"""Disposable browser verification server; never opens the user's library."""
import json
import multiprocessing
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.classroom_server import ClassroomRuntime


def main():
    root = Path(__file__).resolve().parents[1] / "output/playwright"
    root.mkdir(parents=True, exist_ok=True)
    command = root / "command.json"
    command.unlink(missing_ok=True)
    lesson = {"id": "l", "title": "Thảo luận dựa trên bằng chứng", "subject": "Liên môn", "level": 2, "revision": 1,
              "segments": [{"id": "s", "approved": True}],
              "questions": [{"id": "q", "kind": "single", "approved": True,
                             "vi": "Điều gì giúp củng cố một lập luận?", "en": "What supports an argument?", "concept_id": "s", "concept_label": "Bằng chứng", "correct": "A", "rationale_vi": "Dữ liệu có thể kiểm chứng giúp củng cố lập luận.",
                             "options": [{"id": "A", "vi": "Bằng chứng có thể kiểm chứng", "en": "Verifiable evidence"}, {"id": "B", "vi": "Phỏng đoán chưa kiểm tra", "en": "An untested guess"}]}]}
    with tempfile.TemporaryDirectory(prefix="biliclass-browser-") as directory:
        runtime = ClassroomRuntime(directory)
        try:
            info = runtime.start(lesson, {"title": "Lớp thử giao diện", "mode": "anonymous", "size": 50, "host": "127.0.0.1"})
            runtime.request({"action": "open", "question_id": "q", "duration": 1800})
            url = f"http://127.0.0.1:{info['port']}/#join={info['join']}&session={info['session_id']}"
            (root / "preview.json").write_text(json.dumps({"url": url}), encoding="utf-8")
            print(url, flush=True)
            started = time.monotonic()
            while time.monotonic()-started < 1800:
                if command.exists():
                    payload = json.loads(command.read_text(encoding="utf-8-sig"))
                    command.unlink()
                    if payload.get("action") == "stop":
                        break
                    runtime.request(payload)
                time.sleep(.2)
        finally:
            runtime.stop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
