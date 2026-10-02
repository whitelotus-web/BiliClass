import json

import pytest
from fastapi.testclient import TestClient

from app.analytics import delete_session, export_csv, report
from app.classroom_server import admin_app, student_app
from app.classroom_store import ClassroomStore


def lesson():
    return {"id": "lesson", "title": "Bài liên môn", "subject": "Môn tự tạo", "revision": 1, "level": 2,
            "segments": [{"id": "segment", "approved": True}],
            "questions": [{"id": "question", "kind": "single", "approved": True, "vi": "Chọn một ý.", "en": "Choose an idea.",
                           "concept_id": "segment", "concept_label": "Lập luận", "correct": "A",
                           "options": [{"vi": "Ý 1", "en": "Idea 1", "id": "A"}, {"vi": "Ý 2", "en": "Idea 2", "id": "B", "misconception": "Chưa đối chiếu dữ liệu"}]}]}


@pytest.fixture
def classroom(tmp_path):
    store = ClassroomStore(tmp_path / "classroom.db")
    session, join = store.create(lesson(), "Lớp 11A", "seat", 50)
    yield store, session, join
    store.close()


def test_durable_answer_update_duplicate_after_deadline_and_identity(classroom, tmp_path):
    store, session, join = classroom
    student = store.join(session, join, seat=1)
    round_id = store.open_round(session, "question")
    payload = {"round_id": round_id, "answer": "A", "submission_id": "first", "participant_id": "fake"}
    assert not store.submit(session, student["token"], payload)["duplicate"]
    assert store.submit(session, student["token"], payload)["duplicate"]
    store.submit(session, student["token"], {**payload, "submission_id": "second", "answer": "B"})
    state = store.snapshot(session, teacher=True)
    assert state["round"]["answered"] == 1 and state["round"]["counts"] == {"B": 1}
    store.transition(session, "close")
    assert store.submit(session, student["token"], payload)["duplicate"]
    with pytest.raises(ValueError):
        store.submit(session, student["token"], {**payload, "submission_id": "late"})
    with pytest.raises(ValueError):
        store.submit(session, student["token"], {**payload, "answer": "B"})
    reopened = ClassroomStore(tmp_path / "classroom.db")
    assert reopened.join(session, join, student["token"], 1)["participant_id"] == student["participant_id"]
    assert reopened.snapshot(session, student["token"])["round"]["selected"] == "B"
    reopened.close()


def test_no_answer_leak_and_private_server_not_on_student_listener(classroom):
    store, session, join = classroom
    with TestClient(student_app(store, session)) as client:
        assert client.get("/state").status_code == 404
        assert client.post("/action", json={"action": "reveal"}).status_code == 404
        student = client.post("/api/join", json={"join": join, "seat": 1}).json()
        store.open_round(session, "question")
        with client.websocket_connect("/student") as socket:
            socket.send_json({"token": student["token"]})
            data = socket.receive_json()
            serialized = json.dumps(data)
            assert "correct" not in serialized and "misconception" not in serialized and "rationale" not in serialized
        store.transition(session, "close")
        assert "correct" not in store.snapshot(session, student["token"])["round"]
        store.transition(session, "reveal")
        assert store.snapshot(session, student["token"])["round"]["correct"] == "A"
    with TestClient(admin_app(store, session, "secret")) as client:
        assert client.get("/state").status_code == 401
        assert client.get("/state", headers={"Authorization": "Bearer secret"}).status_code == 200


def test_seat_spoof_reveal_while_open_stale_round_and_capacity(classroom):
    store, session, join = classroom
    student = store.join(session, join, seat=1)
    for kwargs in ({"seat": 1}, {"seat": True}, {"seat": 51}, {"reconnect": "made-up"}):
        with pytest.raises(ValueError):
            store.join(session, join, **kwargs)
    round_id = store.open_round(session, "question")
    with pytest.raises(ValueError):
        store.transition(session, "reveal")
    store.transition(session, "close")
    next_round = store.open_round(session, "question", recheck_of=round_id)
    assert next_round != round_id
    with pytest.raises(ValueError):
        store.submit(session, student["token"], {"round_id": round_id, "answer": "A", "submission_id": "stale"})


def test_deadline_server_clock_and_report_denominators(classroom, tmp_path):
    store, session, join = classroom
    one = store.join(session, join, seat=1)
    store.join(session, join, seat=2)
    round_id = store.open_round(session, "question")
    store.submit(session, one["token"], {"round_id": round_id, "answer": "B", "submission_id": "one"})
    store.transition(session, "close")
    data = report(tmp_path, session)
    assert data["rounds"][0]["eligible"] == 2
    assert data["rounds"][0]["answered"] == 1 and data["rounds"][0]["percent"] == 0
    assert data["rounds"][0]["participation"] == 50 and data["concepts"][0]["tone"] == "gray"
    second = store.open_round(session, "question", recheck_of=round_id)
    store.submit(session, one["token"], {"round_id": second, "answer": "A", "submission_id": "two"})
    store.transition(session, "close")
    data = report(tmp_path, session)
    assert data["concepts"][0]["percent"] == 0
    assert data["comparisons"][0]["after"] == 100 and data["comparisons"][0]["same_participants"]
    store.transition(session, "end")
    path = export_csv(tmp_path, session, tmp_path / "Kết quả.csv")
    assert "token" not in path.read_text(encoding="utf-8-sig")
    delete_session(tmp_path, session)
    assert not store.db.execute("SELECT * FROM answers").fetchall()


def test_poll_ungraded_and_unreviewed_question_excluded(tmp_path):
    value = lesson()
    value["questions"][0].update(kind="poll", correct=None)
    value["questions"].append({**value["questions"][0], "id": "unreviewed", "approved": False})
    store = ClassroomStore(tmp_path / "classroom.db")
    session, join = store.create(value, "Khảo sát")
    student = store.join(session, join)
    with pytest.raises(ValueError):
        store.open_round(session, "unreviewed")
    round_id = store.open_round(session, "question")
    store.submit(session, student["token"], {"round_id": round_id, "answer": "B", "submission_id": "poll"})
    store.transition(session, "close")
    data = report(tmp_path, session)
    assert data["rounds"][0]["correct"] is None and data["rounds"][0]["percent"] is None
    assert data["concepts"] == []
    store.close()
