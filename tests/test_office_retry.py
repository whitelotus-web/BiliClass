import time

import pytest

from app.office_retry import call, is_busy


class OfficeBusy(Exception):
    hresult = -2147418111


def test_rejected_com_call_is_retried_without_replaying_a_successful_action():
    attempts = []

    def action():
        attempts.append(True)
        if len(attempts) == 1:
            raise OfficeBusy('Call was rejected by callee')
        return 'done'

    assert call(action) == 'done' and len(attempts) == 2


def test_non_temporary_errors_are_not_retried_or_masked():
    attempts = []
    error = ValueError('Invalid deck')

    def action():
        attempts.append(True)
        raise error

    with pytest.raises(ValueError) as caught:
        call(action)
    assert caught.value is error and len(attempts) == 1


def test_busy_retries_are_bounded_and_known_hresult_forms_are_recognized():
    started = time.monotonic()
    with pytest.raises(OfficeBusy):
        call(lambda: (_ for _ in ()).throw(OfficeBusy()), timeout=.02)
    assert time.monotonic() - started < .3
    assert is_busy(Exception(0x8001010a)) and is_busy(Exception(-2147418111))
    assert not is_busy(Exception('PowerPoint')) and not is_busy(ValueError(5))
