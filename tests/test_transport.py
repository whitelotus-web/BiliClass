import pytest
from fastapi.testclient import TestClient

from biliclass_m0.probes.lan import QuizEngine, create_app


def answer(message="submission-1", option="B"):
    return {"submission_id": message, "answer": option, "question_id": "q-1", "round_id": "round-1"}


def test_idempotency_update_and_reconnect_do_not_increase_counts():
    engine = QuizEngine()
    participant, token = engine.join()
    assert not engine.submit(participant, answer())["duplicate"]
    assert engine.submit(participant, answer())["duplicate"]
    engine.submit(participant, answer("submission-2", "A"))
    assert len(engine.answers) == 1 and engine.answers[participant] == "A"
    assert engine.join(token)[0] == participant
    assert len(engine.participants) == 1
    with pytest.raises(ValueError):
        engine.submit(participant, answer("submission-1", "D"))


def test_closed_and_stale_rounds_are_rejected():
    engine = QuizEngine()
    participant, _ = engine.join()
    with pytest.raises(ValueError):
        engine.submit(participant, {**answer(), "round_id": "old-round"})
    engine.open = False
    with pytest.raises(ValueError):
        engine.submit(participant, answer())
    assert not engine.answers


def test_student_dto_hides_answer_until_reveal():
    engine = QuizEngine()
    assert "correct_answer" not in engine.public_snapshot()
    engine.revealed = True
    assert engine.public_snapshot()["correct_answer"] == "B"


def test_websocket_identity_is_server_assigned_and_invalid_json_is_handled():
    engine = QuizEngine()
    with TestClient(create_app(engine, "test-secret")) as client:
        with client.websocket_connect("/student?join=test-secret") as ws:
            joined = ws.receive_json()
            assert "correct_answer" not in ws.receive_json()
            ws.send_json({**answer(), "participant_id": "someone-else"})
            assert ws.receive_json()["type"] == "ack"
            assert list(engine.answers) == [joined["participant_id"]]
            ws.send_text("not-json")
            assert ws.receive_json()["type"] == "error"


def test_invalid_join_cannot_enter_session():
    from starlette.websockets import WebSocketDisconnect

    engine = QuizEngine()
    with TestClient(create_app(engine, "test-secret")) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/student?join=wrong"):
                pass
    assert not engine.participants
