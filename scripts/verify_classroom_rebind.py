"""Check a resumed class can move ports while retaining one pupil's identity."""

import json
import multiprocessing
import socket
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx
from websockets.sync.client import connect

from app.classroom_server import ClassroomRuntime


def main():
    lesson = {
        "id": "l", "title": "Bài thử liên môn", "subject": "Liên môn", "revision": 1, "level": 2,
        "segments": [{"id": "s", "approved": True}],
        "questions": [{
            "id": "q", "kind": "single", "approved": True, "vi": "Chọn một ý.", "en": "Choose one.",
            "concept_id": "s", "concept_label": "Thảo luận", "correct": "A",
            "options": [{"id": "A", "vi": "Một", "en": "One"}, {"id": "B", "vi": "Hai", "en": "Two"}],
        }],
    }
    with tempfile.TemporaryDirectory(prefix="biliclass-rebind-") as temporary:
        runtime = ClassroomRuntime(temporary)
        holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            info = runtime.start(lesson, {"title": "Lớp thử cổng", "mode": "seat", "size": 30, "host": "127.0.0.1"})
            first_port = info["port"]
            session_id = info["session_id"]
            with httpx.Client(trust_env=False) as client:
                pupil = client.post(f"http://127.0.0.1:{first_port}/api/join",
                                    json={"join": info["join"], "seat": 7}).raise_for_status().json()
            opened = runtime.request({"action": "open", "question_id": "q", "duration": 300})["round"]
            with connect(f"ws://127.0.0.1:{first_port}/student", proxy=None) as web_socket:
                web_socket.send(json.dumps({"token": pupil["token"]}))
                web_socket.recv(timeout=5)
                web_socket.send(json.dumps({"round_id": opened["id"], "answer": "B", "submission_id": "first"}))
                for _ in range(10):
                    if json.loads(web_socket.recv(timeout=5)).get("type") == "ack":
                        break
                else:
                    raise AssertionError("No answer acknowledgement")
            runtime.stop()
            holder.bind(("127.0.0.1", first_port))
            holder.listen(1)
            info = runtime.start({}, {"host": "127.0.0.1", "resume": session_id})
            assert info["network_changed"] and info["port"] != first_port
            assert runtime.request()["round"]["answered"] == 1
            with httpx.Client(trust_env=False) as client:
                response = client.post(f"http://127.0.0.1:{info['port']}/api/join",
                                       json={"join": info["join"], "token": pupil["token"], "seat": 7})
                assert response.status_code == 200, response.text
                recovered = response.json()
                assert recovered["participant_id"] == pupil["participant_id"]
            with connect(f"ws://127.0.0.1:{info['port']}/student", proxy=None) as web_socket:
                web_socket.send(json.dumps({"token": pupil["token"]}))
                snapshot = json.loads(web_socket.recv(timeout=5))
                assert snapshot["round"]["selected"] == "B" and "correct" not in snapshot["round"]
            result = {"status": "passed", "old_port": first_port, "new_port": info["port"],
                      "checks": ["occupied old port recovered", "new QR location signalled",
                                 "same private pupil and seat", "saved answer B and no early correct answer"],
                      "scope": "isolated loopback on current PC, not a school router"}
        finally:
            runtime.stop()
            holder.close()
    target = Path(__file__).resolve().parents[1] / "reports/app/classroom-rebind.json"
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
