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
