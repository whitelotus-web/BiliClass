"""Separate public student and private loopback admin servers in an owned process."""

import asyncio
import collections
import ipaddress
import json
import multiprocessing
import secrets
import socket
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

from .classroom_store import ClassroomStore

WEB_ROOT = Path(__file__).resolve().parent / "student_web"


async def bounded_json(request):
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 16384:
            raise HTTPException(413, "Dữ liệu quá lớn.")
    try:
        value = json.loads(data)
    except ValueError:
        raise HTTPException(400, "Dữ liệu JSON không hợp lệ.") from None
    if not isinstance(value, dict):
        raise HTTPException(400, "Dữ liệu phải là một đối tượng.")
    return value


def same_origin(origin, host):
    return not origin or urlsplit(origin).netloc == host


def student_app(store, session_id):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    joins = collections.defaultdict(collections.deque)
    connections = collections.Counter()

    @app.exception_handler(ValueError)
    async def invalid(_request, error):
        return JSONResponse({"detail": str(error)}, status_code=400)

    @app.middleware("http")
    async def headers(request, call_next):
        if request.method == "POST" and not same_origin(request.headers.get("origin", ""), request.headers.get("host", "")):
            return JSONResponse({"detail": "Nguồn yêu cầu không hợp lệ."}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        return response

    @app.get("/")
    async def index():
        return FileResponse(WEB_ROOT / "index.html")

    @app.get("/app.js")
    async def javascript():
        return FileResponse(WEB_ROOT / "app.js", media_type="text/javascript")

    @app.get("/style.css")
    async def stylesheet():
        return FileResponse(WEB_ROOT / "style.css", media_type="text/css")

    @app.post("/api/join")
    async def join(request: Request):
        payload = await bounded_json(request)
        ip = request.client.host
        timestamps = joins[ip]
        while timestamps and timestamps[0] < time.monotonic() - 60:
            timestamps.popleft()
        if len(timestamps) >= 300:
            raise HTTPException(429, "Hãy chờ một phút rồi tham gia lại.")
        timestamps.append(time.monotonic())
        join_secret, reconnect = payload.get("join", ""), payload.get("token", "")
        if not isinstance(join_secret, str) or not isinstance(reconnect, str) or len(join_secret) > 100 or len(reconnect) > 100:
            raise ValueError("Mã tham gia không hợp lệ.")
        result = store.join(session_id, join_secret, reconnect, payload.get("seat"))
        return {**result, "session_id": session_id}

    @app.websocket("/student")
    async def student(websocket: WebSocket):
        if not same_origin(websocket.headers.get("origin", ""), websocket.headers.get("host", "")):
            await websocket.close(code=1008)
            return
        await websocket.accept()
        identity = None
        registered = False
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=8)
            if len(raw) > 4096:
                await websocket.close(code=1009)
                return
            auth = json.loads(raw)
            token = auth.get("token", "") if isinstance(auth, dict) else ""
            if not isinstance(token, str) or len(token) > 100:
                raise ValueError("Mã kết nối không hợp lệ.")
            identity = store.participant(session_id, token)["id"]
            if connections[identity] >= 3:
                raise ValueError("Đã mở quá nhiều cửa sổ cho người tham gia này.")
            connections[identity] += 1
            registered = True
            last_seq, last_update, sent = -1, 0.0, collections.deque()
            while True:
                snapshot = store.snapshot(session_id, token)
                if snapshot["seq"] != last_seq or time.monotonic() - last_update > 2:
                    await websocket.send_json(snapshot)
                    last_seq, last_update = snapshot["seq"], time.monotonic()
                if snapshot["status"] == "ended":
                    await websocket.close(code=1000)
                    break
                try:
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=0.4)
                except TimeoutError:
                    continue
                if len(raw) > 8192:
                    await websocket.close(code=1009)
                    break
                while sent and sent[0] < time.monotonic() - 10:
                    sent.popleft()
                if len(sent) >= 30:
                    await websocket.close(code=1008)
                    break
                sent.append(time.monotonic())
                try:
                    payload = json.loads(raw)
                    await websocket.send_json(store.submit(session_id, token, payload))
                except (ValueError, TypeError) as exc:
                    await websocket.send_json({"type": "error", "message": str(exc)})
        except (WebSocketDisconnect, TimeoutError):
            pass
        except (ValueError, TypeError):
            await websocket.close(code=1008)
        finally:
            if registered and connections[identity] > 0:
                connections[identity] -= 1
    return app


def admin_app(store, session_id, secret):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def authorized(request, call_next):
        if not secrets.compare_digest(request.headers.get("authorization", ""), "Bearer " + secret):
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)

    @app.exception_handler(ValueError)
    async def invalid(_request, error):
        return JSONResponse({"detail": str(error)}, status_code=400)

    @app.get("/state")
    async def state():
        return store.snapshot(session_id, teacher=True)

    @app.post("/action")
    async def action(request: Request):
        payload = await bounded_json(request)
        action = payload.get("action")
        if action == "open":
            store.open_round(session_id, payload.get("question_id"), payload.get("duration", 60),
                             payload.get("language", "both"), payload.get("recheck_of"))
        else:
            store.transition(session_id, action)
        return store.snapshot(session_id, teacher=True)
    return app


def _serve(directory, lesson, config, secret, events, stop):
    import uvicorn
    store = ClassroomStore(Path(directory) / "classroom.db")
    sockets = []
    try:
        if config.get("resume"):
            session_id = config["resume"]
            join = store.resume(session_id)
        else:
            session_id, join = store.create(lesson, config["title"], config["mode"], config["size"])
        network = store.db.execute("SELECT host,port FROM session_network WHERE session_id=?", (session_id,)).fetchone()
        public_port = config.get("port", network["port"] if network and network["host"] == config["host"] else 0)
        for index, (host, port) in enumerate(((config["host"], public_port), ("127.0.0.1", 0))):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind((host, port))
            except OSError:
                sock.close()
                # A resumed class keeps its browser origin when possible. If
                # another program took that port, issue a new QR on a free
                # port; each pupil can use their private recovery code there.
                if index != 0 or not config.get("resume") or not port or config.get("port") is not None:
                    raise
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((host, 0))
            sock.listen(256)
            sockets.append(sock)
        network_changed = bool(network and (network["host"] != config["host"] or network["port"] != sockets[0].getsockname()[1]))
        with store.db:
            store.db.execute("INSERT INTO session_network VALUES(?,?,?) ON CONFLICT(session_id) DO UPDATE SET host=excluded.host,port=excluded.port", (session_id, config["host"], sockets[0].getsockname()[1]))
        # A windowed Windows executable has no sys.stdout/stderr. Uvicorn's
        # default color formatter probes those streams during configuration.
        public = uvicorn.Server(uvicorn.Config(student_app(store, session_id), log_config=None, log_level="error", access_log=False,
                                               ws="websockets-sansio", ws_max_size=8192))
        private = uvicorn.Server(uvicorn.Config(admin_app(store, session_id, secret), log_config=None, log_level="error", access_log=False))

        async def run():
            async def monitor():
                while not (public.started and private.started):
                    await asyncio.sleep(0.05)
                events.put({"session_id": session_id, "join": join, "host": config["host"],
                            "port": sockets[0].getsockname()[1], "admin_port": sockets[1].getsockname()[1],
                            "network_changed": network_changed})
                while not stop.is_set():
                    await asyncio.sleep(0.1)
                public.should_exit = private.should_exit = True
            await asyncio.gather(public.serve(sockets=[sockets[0]]), private.serve(sockets=[sockets[1]]), monitor())
        asyncio.run(run())
    except Exception as exc:
        events.put({"error": str(exc)})
    finally:
        for sock in sockets:
            sock.close()
        store.close()


class ClassroomRuntime:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.process = None
        self.info = {}
        self.secret = secrets.token_urlsafe(32)
        self.lock = threading.Lock()

    def start(self, lesson, config):
        ip = ipaddress.ip_address(config["host"])
        if ip.version != 4 or not (ip.is_private or ip.is_loopback):
            raise ValueError("Chọn địa chỉ IPv4 của mạng nội bộ.")
        context = multiprocessing.get_context("spawn")
        self.stop_event, events = context.Event(), context.Queue()
        self.process = context.Process(target=_serve, args=(str(self.directory), lesson, config, self.secret, events, self.stop_event), daemon=True)
        self.process.start()
        try:
            self.info = events.get(timeout=25)
            if "error" in self.info:
                raise ValueError(self.info["error"])
            return self.info
        except Exception:
            self.stop()
            raise
        finally:
            events.close()

    def request(self, payload=None):
        with self.lock:
            if not self.process or not self.process.is_alive():
                raise ValueError("Máy chủ lớp học đã dừng. Có thể mở lại phiên từ Báo cáo.")
            base = f"http://127.0.0.1:{self.info['admin_port']}"
            with httpx.Client(timeout=3, trust_env=False, headers={"Authorization": "Bearer " + self.secret}) as client:
                response = client.get(base + "/state") if payload is None else client.post(base + "/action", json=payload)
            data = response.json()
            if response.status_code != 200:
                raise ValueError(data.get("detail", "Máy chủ lớp học không phản hồi."))
            return data

    def stop(self):
        if self.process:
            self.stop_event.set()
            self.process.join(timeout=5)
            if self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout=2)
            self.process = None
