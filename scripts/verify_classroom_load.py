"""50 real loopback WebSocket clients, isolated database and server process."""
import asyncio
import json
import multiprocessing
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from websockets.asyncio.client import connect

from app.analytics import report
from app.classroom_server import ClassroomRuntime


async def exercise(runtime, info):
    base = f"http://127.0.0.1:{info['port']}"
    async with httpx.AsyncClient(trust_env=False, timeout=15) as client:
        replies = await asyncio.gather(*(client.post(base + "/api/join", json={"join": info["join"], "seat": n+1}) for n in range(50)))
        assert all(r.status_code == 200 for r in replies), [r.status_code for r in replies]
        students = [r.json() for r in replies]
        assert (await client.get(base + "/state")).status_code == 404
        assert (await client.get(f"http://127.0.0.1:{info['admin_port']}/state")).status_code == 401
    state = await asyncio.to_thread(runtime.request, {"action": "open", "question_id": "q", "duration": 120, "language": "both"})
    round_id = state["round"]["id"]
    latencies = []
    connected = 0
    gate = asyncio.Event()

    async def student_flow(index, student):
        nonlocal connected
        async with connect(base.replace("http", "ws") + "/student", proxy=None) as ws:
            await ws.send(json.dumps({"token": student["token"]}))
            first = json.loads(await ws.recv())
            assert not {"correct", "rationale_vi", "misconception"} & set(first["round"])
            connected += 1
            if connected == 50:
                gate.set()
            await asyncio.wait_for(gate.wait(), 20)
            payload = {"round_id": round_id, "submission_id": f"m{index}", "answer": "A" if index < 35 else "B"}
            start = time.perf_counter()
            await ws.send(json.dumps(payload))
            while True:
                reply = json.loads(await asyncio.wait_for(ws.recv(), 15))
                if reply["type"] == "ack":
                    break
            latencies.append(time.perf_counter()-start)
            await ws.send(json.dumps(payload))
            while True:
                reply = json.loads(await ws.recv())
                if reply["type"] == "ack":
                    assert reply["duplicate"]
                    break
        async with connect(base.replace("http", "ws") + "/student", proxy=None) as ws:
            await ws.send(json.dumps({"token": student["token"]}))
            reconnected = json.loads(await ws.recv())
            assert reconnected["round"]["selected"] == payload["answer"]
    await asyncio.gather(*(student_flow(i, s) for i, s in enumerate(students)))
    state = await asyncio.to_thread(runtime.request)
    assert state["round"]["answered"] == 50 and state["round"]["counts"] == {"A": 35, "B": 15}, state
    await asyncio.to_thread(runtime.request, {"action": "close"})
    await asyncio.to_thread(runtime.request, {"action": "reveal"})
    return {"clients": 50, "answered": 50, "correct": 35, "duplicate_and_reconnect": True,
            "ack_p95_ms": round(sorted(latencies)[47]*1000, 1), "max_ack_ms": round(max(latencies)*1000, 1)}


def main():
    lesson = {"id": "l", "title": "Kiểm thử đa môn", "subject": "Liên môn", "revision": 1, "level": 2,
              "segments": [{"id": "s", "approved": True}],
              "questions": [{"id": "q", "kind": "single", "approved": True, "vi": "Chọn bằng chứng.", "en": "Choose the evidence.",
                             "concept_id": "s", "concept_label": "Bằng chứng", "correct": "A",
                             "options": [{"id": "A", "vi": "Dữ liệu", "en": "Data"}, {"id": "B", "vi": "Phỏng đoán", "en": "Guess"}]}]}
    with tempfile.TemporaryDirectory(prefix="biliclass-load-") as temporary:
        runtime = ClassroomRuntime(temporary)
        try:
            info = runtime.start(lesson, {"title": "50 học sinh mô phỏng", "mode": "seat", "size": 50, "host": "127.0.0.1"})
            result = asyncio.run(exercise(runtime, info))
            previous_port = info["port"]
            runtime.stop()
            info = runtime.start({}, {"host": "127.0.0.1", "resume": info["session_id"]})
            assert info["port"] == previous_port
            assert runtime.request()["round"]["answered"] == 50
            runtime.request({"action": "end"})
            data = report(temporary, info["session_id"])
            assert data["rounds"][0]["percent"] == 70
            result.update(restart_persists=True, report_percent=70, scope="Loopback on this PC; not a physical Wi-Fi trial")
        finally:
            runtime.stop()
    path = Path(__file__).resolve().parents[1] / "reports/app/classroom-load.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
