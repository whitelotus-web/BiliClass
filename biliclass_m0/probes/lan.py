"""In-memory transport spike. Durable sessions are intentionally left to M5."""

import asyncio
import json
import secrets
import socket
import statistics
import threading
import time
from datetime import datetime, timezone

import uvicorn
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ..contracts import WebQuizProvider


class QuizEngine:
    def __init__(self):
        self.participants: dict[str, str] = {}
        self.answers: dict[str, str] = {}
        self.messages: dict[tuple[str, str], str] = {}
        self.provider = WebQuizProvider()
        self.open = True
        self.revealed = False

    def join(self, reconnect_token: str = "") -> tuple[str, str]:
        if reconnect_token:
            if reconnect_token not in self.participants:
                raise ValueError("Invalid reconnect token")
            return self.participants[reconnect_token], reconnect_token
        token, participant = secrets.token_urlsafe(24), secrets.token_hex(8)
        self.participants[token] = participant
        return participant, token

    def public_snapshot(self) -> dict:
        value = {
            "type": "snapshot",
            "round_id": "round-1",
            "question_id": "q-1",
            "prompt": "Chọn phương án B để thử đường truyền.",
            "options": ["A", "B", "C", "D"],
            "answered": len(self.answers),
            "joined": len(self.participants),
            "open": self.open,
        }
        if self.revealed:
            value["correct_answer"] = "B"
        return value

    def submit(self, participant: str, payload: dict) -> dict:
        if payload.get("round_id") != "round-1" or payload.get("question_id") != "q-1":
            raise ValueError("Question round does not match")
        if not self.open:
            raise ValueError("Question is closed")
        answer = payload.get("answer")
        message = payload.get("submission_id")
        if answer not in ("A", "B", "C", "D") or not isinstance(message, str) or not 1 <= len(message) <= 80:
            raise ValueError("Invalid answer or submission ID")
        identity = (participant, message)
        if identity in self.messages and self.messages[identity] != answer:
            raise ValueError("Submission ID reused with different answer")
        normalized = self.provider.normalize(
            {
                "participant_id": participant,
                "question_id": "q-1",
                "round_id": "round-1",
                "answer": answer,
                "submission_id": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        duplicate = identity in self.messages
        if not duplicate:
            self.answers[normalized.participant_id] = normalized.answer
            self.messages[identity] = answer
        return {
            "type": "ack",
            "submission_id": message,
            "duplicate": duplicate,
            "answered": len(self.answers),
        }


def create_app(engine: QuizEngine, join_secret: str) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/health")
    def health():
        return {"status": "ready", "experiment": "BiliClass M0"}

    @app.websocket("/student")
    async def student(websocket: WebSocket):
        if not secrets.compare_digest(websocket.query_params.get("join", ""), join_secret):
            await websocket.close(code=1008)
            return
        try:
            participant, token = engine.join(websocket.query_params.get("resume", ""))
        except ValueError:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        await websocket.send_json({"type": "joined", "participant_id": participant, "reconnect_token": token})
        await websocket.send_json(engine.public_snapshot())
        try:
            while True:
                raw = await websocket.receive_text()
                if len(raw) > 8192:
                    await websocket.close(code=1009)
                    return
                try:
                    payload = json.loads(raw)
                    if not isinstance(payload, dict):
                        raise ValueError("Expected object")
                    result = engine.submit(participant, payload)
                    await websocket.send_json(result)
                except (ValueError, KeyError) as exc:
                    await websocket.send_json({"type": "error", "message": str(exc)})
        except WebSocketDisconnect:
            pass

    return app


async def exercise(port: int, secret: str, count: int) -> dict:
    connected = 0
    ready = asyncio.Event()
    latencies = []
    resume_data = []
    no_leak = []
    duplicate_acks = []
    url = f"ws://127.0.0.1:{port}/student?join={secret}"

    async def client(index):
        nonlocal connected
        async with websockets.connect(url, proxy=None) as ws:
            joined = json.loads(await ws.recv())
            snapshot = json.loads(await ws.recv())
            no_leak.append("correct_answer" not in snapshot and "misconceptions" not in snapshot)
            resume_data.append(joined)
            connected += 1
            if connected == count:
                ready.set()
            await asyncio.wait_for(ready.wait(), timeout=20)
            payload = {
                "submission_id": f"submit-{index}",
                "round_id": "round-1",
                "question_id": "q-1",
                "answer": "B",
                "participant_id": "spoofed-id-is-ignored",
            }
            start = time.perf_counter()
            await ws.send(json.dumps(payload))
            ack = json.loads(await ws.recv())
            if ack.get("type") != "ack":
                raise RuntimeError(str(ack))
            latencies.append((time.perf_counter() - start) * 1000)
            await ws.send(json.dumps(payload))
            duplicate_acks.append(json.loads(await ws.recv()).get("duplicate", False))

    await asyncio.gather(*(client(i) for i in range(count)))
    previous = resume_data[0]
    async with websockets.connect(url + "&resume=" + previous["reconnect_token"], proxy=None) as ws:
        resumed = json.loads(await ws.recv())
        await ws.recv()
    return {
        "simultaneous_clients": count,
        "responses": len(latencies),
        "ack_p95_ms": round(statistics.quantiles(latencies, n=100)[94], 2),
        "ack_max_ms": round(max(latencies), 2),
        "no_answer_leak": all(no_leak),
        "duplicate_acknowledged": all(duplicate_acks),
        "reconnect_same_participant": resumed["participant_id"] == previous["participant_id"],
    }


def run() -> dict:
    engine = QuizEngine()
    secret = secrets.token_urlsafe(32)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    config = uvicorn.Config(
        create_app(engine, secret),
        log_level="error",
        ws="websockets-sansio",
        ws_max_size=8192,
        access_log=False,
    )
    server = uvicorn.Server(config)
    worker = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    worker.start()
    try:
        for _ in range(100):
            if server.started:
                break
            time.sleep(0.05)
        if not server.started:
            raise RuntimeError("Local server failed to start")
        measured = asyncio.run(exercise(port, secret, 50))
        checks = (
            measured["no_answer_leak"],
            measured["duplicate_acknowledged"],
            measured["reconnect_same_participant"],
            len(engine.answers) == 50,
            len(engine.participants) == 50,
        )
        return {
            "status": "passed" if all(checks) else "failed",
            **measured,
            "unique_answers": len(engine.answers),
            "unique_participants": len(engine.participants),
            "scope": "50 WebSocket clients trên loopback, không phải 50 điện thoại qua Wi-Fi.",
            "pending": [
                "Điện thoại Android/iPhone trên LAN thật",
                "Firewall/router/client isolation",
                "Dashboard broadcast latency",
                "Ghi SQLite và khôi phục process ở M5",
            ],
        }
    finally:
        server.should_exit = True
        worker.join(timeout=5)
        sock.close()
