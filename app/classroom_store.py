"""Durable classroom state. Only approved snapshots enter a teaching session."""

import hashlib
import json
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from uuid import uuid4


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class ClassroomStore:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.directory = Path(path).parent
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=5000")
        if self.db.execute("PRAGMA user_version").fetchone()[0] > 1:
            self.db.close()
            raise ValueError("Database lớp học cần phiên bản BiliClass mới hơn.")
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,title TEXT NOT NULL,lesson TEXT NOT NULL,
                mode TEXT NOT NULL,size INTEGER NOT NULL,join_hash TEXT NOT NULL,status TEXT NOT NULL,
                current_round TEXT,created REAL NOT NULL,ended REAL,seq INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS participants(id TEXT PRIMARY KEY,session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,seat INTEGER,joined REAL NOT NULL,UNIQUE(session_id,seat));
            CREATE TABLE IF NOT EXISTS rounds(id TEXT PRIMARY KEY,session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                question TEXT NOT NULL,language TEXT NOT NULL,status TEXT NOT NULL,deadline REAL NOT NULL,
                opened REAL NOT NULL,closed REAL,eligible INTEGER,recheck_of TEXT REFERENCES rounds(id));
            CREATE TABLE IF NOT EXISTS answers(round_id TEXT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
                participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,option_id TEXT NOT NULL,
                submission_id TEXT NOT NULL,updated REAL NOT NULL,PRIMARY KEY(round_id,participant_id));
            CREATE TABLE IF NOT EXISTS submissions(session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,message_id TEXT NOT NULL,
                round_id TEXT NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,option_id TEXT NOT NULL,
                PRIMARY KEY(session_id,participant_id,message_id));
            CREATE TABLE IF NOT EXISTS session_network(session_id TEXT PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
                host TEXT NOT NULL,port INTEGER NOT NULL);
            PRAGMA user_version=1;
        ''')

    def close(self):
        self.db.close()

    def session(self, identity):
        row = self.db.execute("SELECT * FROM sessions WHERE id=?", (identity,)).fetchone()
        if not row:
            raise ValueError("Không tìm thấy phiên học.")
        return row

    def bump(self, session_id):
        self.db.execute("UPDATE sessions SET seq=seq+1 WHERE id=?", (session_id,))

    def create(self, lesson, title, mode="anonymous", size=50):
        from .content import validate_question
        from .readiness import preparation_current, text_readiness
        if mode not in {"anonymous", "seat"} or type(size) is not int or not 1 <= size <= 200:
            raise ValueError("Chế độ lớp hoặc sĩ số không hợp lệ (1–200).")
        if not isinstance(title, str) or not title.strip() or len(title) > 150:
            raise ValueError("Điền tên lớp/tiết học tối đa 150 ký tự.")
        approved = {s["id"] for s in lesson.get("segments", []) if s.get("approved")}
        if not approved:
            raise ValueError("Duyệt nội dung bài trước khi bắt đầu lớp.")
        if any("vi" in segment or "en" in segment for segment in lesson["segments"]):
            if not text_readiness(lesson, self.directory)["text_ready"] or not preparation_current(lesson):
                raise ValueError("Bài cần được duyệt đầy đủ và chốt bản chuẩn bị hiện tại trước khi mở lớp.")
        questions = []
        for q in lesson.get("questions", []):
            if q.get("approved") and q.get("concept_id") in approved:
                clean = validate_question(q)
                clean["id"] = q["id"]
                questions.append(clean)
        snapshot = {"id": lesson["id"], "title": lesson["title"], "subject": lesson["subject"],
                    "revision": lesson["revision"], "level": lesson.get("level", 2),
                    "grade": lesson.get("grade", ""), "teaching_preset": lesson.get("teaching_preset", "standard"),
                    "questions": questions}
        identity, join = str(uuid4()), secrets.token_urlsafe(24)
        with self.lock, self.db:
            self.db.execute("INSERT INTO sessions(id,title,lesson,mode,size,join_hash,status,created) VALUES(?,?,?,?,?,?,?,?)",
                            (identity, title.strip(), json.dumps(snapshot, ensure_ascii=False), mode, size, digest(join), "active", time.time()))
        return identity, join

    def resume(self, session_id):
        join = secrets.token_urlsafe(24)
        with self.lock, self.db:
            session = self.session(session_id)
            if session["status"] == "ended":
                raise ValueError("Phiên đã kết thúc. Tạo phiên mới để dạy tiếp.")
            self.expire(session_id)
            self.db.execute("UPDATE sessions SET join_hash=? WHERE id=?", (digest(join), session_id))
            self.bump(session_id)
        return join

    def join(self, session_id, join_secret, reconnect="", seat=None):
        with self.lock, self.db:
            session = self.session(session_id)
            if session["status"] != "active" or not secrets.compare_digest(session["join_hash"], digest(join_secret)):
                raise ValueError("Mã lớp không hợp lệ hoặc phiên đã kết thúc.")
            if reconnect:
                row = self.db.execute("SELECT id,seat FROM participants WHERE session_id=? AND token_hash=?",
                                      (session_id, digest(reconnect))).fetchone()
                if not row:
                    raise ValueError("Không thể khôi phục chỗ ngồi từ mã này.")
                return {"participant_id": row["id"], "token": reconnect, "seat": row["seat"]}
            count = self.db.execute("SELECT count(*) FROM participants WHERE session_id=?", (session_id,)).fetchone()[0]
            if count >= session["size"]:
                raise ValueError("Lớp đã đủ số người tham gia.")
            if session["mode"] == "seat":
                if type(seat) is not int or not 1 <= seat <= session["size"]:
                    raise ValueError(f"Chọn số chỗ từ 1 đến {session['size']}.")
                if self.db.execute("SELECT 1 FROM participants WHERE session_id=? AND seat=?", (session_id, seat)).fetchone():
                    raise ValueError("Chỗ này đã có người. Dùng lại trình duyệt cũ hoặc chọn chỗ khác.")
            else:
                seat = None
            identity, token = str(uuid4()), secrets.token_urlsafe(32)
            self.db.execute("INSERT INTO participants VALUES(?,?,?,?,?)", (identity, session_id, digest(token), seat, time.time()))
            self.bump(session_id)
            return {"participant_id": identity, "token": token, "seat": seat}

    def participant(self, session_id, token):
        row = self.db.execute("SELECT * FROM participants WHERE session_id=? AND token_hash=?", (session_id, digest(token))).fetchone()
        if not row:
            raise ValueError("Phiên tham gia không hợp lệ.")
        return row

    def expire(self, session_id):
        session = self.session(session_id)
        if session["current_round"]:
            round_row = self.db.execute("SELECT * FROM rounds WHERE id=?", (session["current_round"],)).fetchone()
            if round_row and round_row["status"] == "open" and time.time() >= round_row["deadline"]:
                self._close_round(session_id, round_row["id"], round_row["deadline"])

    def _close_round(self, session_id, round_id, closed_at):
        eligible = self.db.execute("SELECT count(*) FROM participants WHERE session_id=? AND joined<=?", (session_id, closed_at)).fetchone()[0]
        self.db.execute("UPDATE rounds SET status='closed',closed=?,eligible=? WHERE id=? AND status='open'", (closed_at, eligible, round_id))
        self.bump(session_id)

    def open_round(self, session_id, question_id, duration=60, language="both", recheck_of=None):
        if type(duration) is not int or not 5 <= duration <= 3600 or language not in {"vi", "en", "both"}:
            raise ValueError("Chọn thời gian 5–3.600 giây và ngôn ngữ hợp lệ.")
        with self.lock, self.db:
            self.expire(session_id)
            session = self.session(session_id)
            if session["status"] != "active":
                raise ValueError("Phiên đã kết thúc.")
            current = self.db.execute("SELECT status FROM rounds WHERE id=?", (session["current_round"],)).fetchone()
            if current and current[0] == "open":
                raise ValueError("Đóng câu đang mở trước khi chuyển câu khác.")
            question = next((q for q in json.loads(session["lesson"])["questions"] if q["id"] == question_id), None)
            if not question:
                raise ValueError("Câu hỏi không nằm trong bản đã duyệt của phiên.")
            if recheck_of:
                previous = self.db.execute("SELECT * FROM rounds WHERE id=? AND session_id=?", (recheck_of, session_id)).fetchone()
                if not previous or json.loads(previous["question"])["id"] != question_id:
                    raise ValueError("Kiểm tra lại phải liên kết đúng câu trong cùng phiên.")
            identity, opened = str(uuid4()), time.time()
            self.db.execute("INSERT INTO rounds(id,session_id,question,language,status,deadline,opened,recheck_of) VALUES(?,?,?,?,?,?,?,?)",
                            (identity, session_id, json.dumps(question, ensure_ascii=False), language, "open", opened + duration, opened, recheck_of))
            self.db.execute("UPDATE sessions SET current_round=?,seq=seq+1 WHERE id=?", (identity, session_id))
            return identity

    def transition(self, session_id, action):
        with self.lock, self.db:
            self.expire(session_id)
            session = self.session(session_id)
            if action == "end":
                if session["current_round"]:
                    self._close_round(session_id, session["current_round"], time.time())
                self.db.execute("UPDATE sessions SET status='ended',ended=?,seq=seq+1 WHERE id=?", (time.time(), session_id))
                return
            row = self.db.execute("SELECT * FROM rounds WHERE id=?", (session["current_round"],)).fetchone()
            if not row:
                raise ValueError("Chưa mở câu hỏi.")
            if action == "close":
                if row["status"] == "open":
                    self._close_round(session_id, row["id"], time.time())
            elif action == "reveal":
                if row["status"] == "open":
                    raise ValueError("Đóng câu hỏi trước khi công bố đáp án.")
                self.db.execute("UPDATE rounds SET status='revealed' WHERE id=?", (row["id"],))
                self.bump(session_id)
            else:
                raise ValueError("Thao tác phiên không hợp lệ.")

    def submit(self, session_id, token, payload):
        with self.lock, self.db:
            participant = self.participant(session_id, token)
            if not isinstance(payload, dict):
                raise ValueError("Câu trả lời không hợp lệ.")
            message, round_id, answer = payload.get("submission_id"), payload.get("round_id"), payload.get("answer")
            if not all(isinstance(v, str) and 1 <= len(v) <= 100 for v in (message, round_id, answer)):
                raise ValueError("Câu trả lời thiếu mã gửi, mã lượt hoặc lựa chọn.")
            previous = self.db.execute("SELECT * FROM submissions WHERE session_id=? AND participant_id=? AND message_id=?",
                                       (session_id, participant["id"], message)).fetchone()
            if previous:
                if (previous["round_id"], previous["option_id"]) != (round_id, answer):
                    raise ValueError("Mã gửi đã dùng cho câu trả lời khác.")
                return {"type": "ack", "submission_id": message, "round_id": round_id, "answer": answer, "duplicate": True}
            self.expire(session_id)
            session = self.session(session_id)
            row = self.db.execute("SELECT * FROM rounds WHERE id=? AND session_id=?", (round_id, session_id)).fetchone()
            if session["status"] != "active" or session["current_round"] != round_id or not row or row["status"] != "open":
                raise ValueError("Câu hỏi đã đóng hoặc lượt trả lời không còn hiện hành.")
            question = json.loads(row["question"])
            if answer not in {option["id"] for option in question["options"]}:
                raise ValueError("Lựa chọn không có trong câu hỏi.")
            self.db.execute("INSERT INTO submissions VALUES(?,?,?,?,?)", (session_id, participant["id"], message, round_id, answer))
            self.db.execute("INSERT INTO answers VALUES(?,?,?,?,?) ON CONFLICT(round_id,participant_id) DO UPDATE SET option_id=excluded.option_id,submission_id=excluded.submission_id,updated=excluded.updated",
                            (round_id, participant["id"], answer, message, time.time()))
            self.bump(session_id)
            return {"type": "ack", "submission_id": message, "round_id": round_id, "answer": answer, "duplicate": False}

    def snapshot(self, session_id, token=None, teacher=False):
        with self.lock, self.db:
            self.expire(session_id)
            session = self.session(session_id)
            participant = self.participant(session_id, token) if token else None
            if not teacher and participant is None:
                raise ValueError("Cần tham gia lớp trước.")
            count = self.db.execute("SELECT count(*) FROM participants WHERE session_id=?", (session_id,)).fetchone()[0]
            result = {"type": "snapshot", "version": 1, "session_id": session_id, "title": session["title"],
                      "status": session["status"], "joined": count, "capacity": session["size"],
                      "seq": session["seq"], "server_time": time.time(), "round": None}
            row = self.db.execute("SELECT * FROM rounds WHERE id=?", (session["current_round"],)).fetchone()
            if row:
                question = json.loads(row["question"])
                round_value = {"id": row["id"], "status": row["status"], "deadline": row["deadline"],
                               "language": row["language"], "kind": question["kind"], "vi": question["vi"], "en": question["en"],
                               "options": [{k: option[k] for k in ("id", "vi", "en")} for option in question["options"]]}
                if participant:
                    selected = self.db.execute("SELECT option_id FROM answers WHERE round_id=? AND participant_id=?", (row["id"], participant["id"])).fetchone()
                    round_value["selected"] = selected[0] if selected else None
                if teacher or row["status"] == "revealed":
                    round_value.update(correct=question["correct"], rationale_vi=question["rationale_vi"], rationale_en=question["rationale_en"])
                if teacher:
                    counts = dict(self.db.execute("SELECT option_id,count(*) FROM answers WHERE round_id=? GROUP BY option_id", (row["id"],)).fetchall())
                    round_value.update(counts=counts, answered=sum(counts.values()), eligible=row["eligible"] if row["eligible"] is not None else count,
                                       question_id=question["id"], recheck_of=row["recheck_of"], concept=question["concept_label"])
                result["round"] = round_value
            if teacher:
                result["questions"] = json.loads(session["lesson"])["questions"]
                result["mode"] = session["mode"]
            return result
