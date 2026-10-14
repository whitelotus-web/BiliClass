import json

from app.browser_wait import ResponseWait


def test_reconnect_and_reopen_share_one_response_budget(tmp_path, monkeypatch):
    clock=[100.0]
    monkeypatch.setattr('app.browser_wait.time.monotonic',lambda:clock[0])
    record={'send_sha256':'a'*64}
    with ResponseWait(tmp_path,record,900) as wait:
        clock[0]+=600
        assert wait.checkpoint()==300
    reopened=json.loads((tmp_path/'browser-job.json').read_text())
    clock[0]+=3600  # Time while paused is not counted as processing.
    with ResponseWait(tmp_path,reopened,900) as wait:
        assert wait.checkpoint()==300
        clock[0]+=300
        assert wait.checkpoint()==0 and reopened['wait_exhausted']
    with ResponseWait(tmp_path,reopened,900) as wait:
        assert wait.checkpoint()==0


def test_only_a_new_confirmed_submission_gets_another_wait_budget(tmp_path,monkeypatch):
    clock=[100.0]
    monkeypatch.setattr('app.browser_wait.time.monotonic',lambda:clock[0])
    record={'send_sha256':'a'*64,'response_wait':{'key':'a'*64,'seconds':900},'wait_exhausted':True}
    with ResponseWait(tmp_path,record,900) as wait:
        assert wait.checkpoint()==0
        record['send_sha256']='b'*64
        assert wait.checkpoint()==900 and not record['wait_exhausted']
        clock[0]+=15
    assert record['response_wait']['seconds']==15


def test_wait_elapsed_persists_when_network_raises(tmp_path,monkeypatch):
    clock=[100.0]
    monkeypatch.setattr('app.browser_wait.time.monotonic',lambda:clock[0])
    record={'send_sha256':'a'*64}
    try:
        with ResponseWait(tmp_path,record,900):
            clock[0]+=12
            raise RuntimeError('Network')
    except RuntimeError:
        pass
    assert json.loads((tmp_path/'browser-job.json').read_text())['response_wait']['seconds']==12


def test_active_turn_extends_at_fifteen_minutes_and_resume_keeps_that_window(tmp_path, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr('app.browser_wait.time.monotonic', lambda: clock[0])
    record = {'send_sha256': 'a'*64, 'response_wait': {'key': 'a'*64, 'seconds': 900, 'limit': 900}}
    with ResponseWait(tmp_path, record, 900) as wait:
        assert wait.extend_active(True)
        assert wait.checkpoint() == 300 and not record['wait_exhausted']
        clock[0] += 100
    clock[0] += 1800
    with ResponseWait(tmp_path, record, 900) as wait:
        assert wait.checkpoint() == 200
        clock[0] += 200
        assert not wait.extend_active(False)
        assert record['wait_exhausted']


def test_active_turn_extensions_have_a_durable_absolute_cap(tmp_path, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr('app.browser_wait.time.monotonic', lambda: clock[0])
    record = {'send_sha256': 'a'*64, 'response_wait': {'key': 'a'*64, 'seconds': 3500, 'limit': 3500, 'base_limit': 900}}
    with ResponseWait(tmp_path, record, 900) as wait:
        assert wait.extend_active(True) and wait.checkpoint() == 100
        clock[0] += 100
        assert not wait.extend_active(True)
    with ResponseWait(tmp_path, record, 900) as wait:
        assert not wait.extend_active(True)


def test_short_custom_wait_stays_strict_and_new_turn_resets_extensions(tmp_path, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr('app.browser_wait.time.monotonic', lambda: clock[0])
    record = {'send_sha256': 'a'*64}
    with ResponseWait(tmp_path, record, 1) as wait:
        clock[0] += 1
        assert not wait.extend_active(True)
    record['response_wait'] = {'key': 'a'*64, 'seconds': 900, 'limit': 1200, 'base_limit': 900}
    with ResponseWait(tmp_path, record, 900) as wait:
        record['send_sha256'] = 'b'*64
        assert wait.checkpoint() == 900


def test_silent_response_refreshes_are_bounded_across_reconnects():
    from app.browser_wait import stale_refresh

    record = {'response_wait': {'key': 'one', 'seconds': 0}}
    assert not stale_refresh(record, 'working', generating=True)
    for value in (180, 360, 540):
        record['response_wait']['seconds'] = value
        assert stale_refresh(record, 'working', generating=True)
        record = json.loads(json.dumps(record))
    record['response_wait']['seconds'] = 900
    assert not stale_refresh(record, 'working', generating=True)
    assert record['response_watch']['refreshes'] == 3
    assert not stale_refresh(record, 'changed', generating=True)
    record['response_wait'] = {'key': 'new-turn', 'seconds': 0}
    assert not stale_refresh(record, 'working', generating=True)
    record['response_wait']['seconds'] = 180
    assert stale_refresh(record, 'working', generating=True)
