from app.conversion_presentation import STAGE_COPY, display_state


def test_active_progress_keeps_evidence_but_displays_teacher_copy():
    for stage in STAGE_COPY:
        raw = {"running": True, "stage": stage, "message": "Internal browser prompt sent", "percent": 25}
        shown = display_state(raw)
        assert shown["message"] == raw["message"] and shown["percent"] == 25
        assert all(word not in shown["displayMessage"].casefold() for word in ["browser", "prompt", "chatgpt"])
        assert "displayMessage" not in raw


def test_stopped_receipt_never_claims_work_is_still_running():
    shown = display_state({"running": False, "phase": "error", "errorCode": "receipt", "stage": "session"})
    assert "tạm dừng" in shown["displayMessage"]
    assert shown["displayStage"] == "Chuyển đổi tạm dừng"


def test_account_action_and_completion_remain_truthful():
    for code in ["login", "verification", "limit"]:
        shown = display_state({"running": False, "phase": "error", "errorCode": code})
        assert "tự động xử lý" not in shown["displayMessage"]
    assert "xác minh" in display_state({"phase": "error", "errorCode": "verification"})["displayMessage"]
    assert "hết lượt" in display_state({"phase": "error", "errorCode": "limit"})["displayMessage"]
    assert "Đã lưu" in display_state({"phase": "completed"})["displayStage"]
