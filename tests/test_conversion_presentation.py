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


def test_failed_file_transfer_does_not_claim_completion_or_expired_login():
    shown = display_state({'running': False, 'phase': 'error', 'errorCode': 'file_transfer',
                           'stage': 'download', 'percent': 55})
    assert 'chưa hoàn tất' in shown['displayMessage']
    assert 'đăng nhập' not in shown['displayMessage']
    assert shown['percent'] == 55 and shown['displayStage'] == 'Chuyển đổi tạm dừng'


def test_cancel_requested_and_discarded_states_do_not_claim_creation_or_resume():
    stopping = display_state({'running': True, 'stopping': True, 'stage': 'translate', 'percent': 40})
    assert 'Đang hủy' in stopping['displayStage'] and stopping['percent'] == 40
    discarded = display_state({'running': False, 'phase': 'discarded', 'stage': 'save'})
    assert 'Đã hủy' in discarded['displayStage'] and 'bài giảng mới' in discarded['displayMessage']


def test_stop_keeps_progress_and_does_not_describe_deleting_the_work():
    stopping = display_state({'running': True, 'stopping': True, 'stopRequested': True,
                              'stage': 'translate', 'percent': 40})
    assert stopping['displayStage'] == 'Đang dừng chuyển đổi' and stopping['percent'] == 40
    assert 'giữ lại' in stopping['displayMessage'] and 'xóa' not in stopping['displayMessage']


def test_translation_setup_errors_show_specific_action_without_unrelated_azure_region():
    for code, marker in [('api_billing','Free'), ('api_deployment','doPost'), ('api_model','model')]:
        shown = display_state(dict(running=False, phase='error', errorCode=code, percent=26))
        assert marker in shown['displayMessage'] and shown['percent'] == 26
        assert 'Azure' not in shown['displayMessage']
