from threading import Event

import pytest

from app.browser_accounts import BrowserAccounts
from app.browser_automation import BrowserProblem, read_record, write_record
from app.browser_dispatch import convert_available


def accounts_fixture(tmp_path):
    store = BrowserAccounts(tmp_path / "library")
    plus, free = store.add("Plus"), store.add("Free")
    store.observe(plus["id"], "plus")
    store.observe(free["id"], "free")
    return store, plus["id"], free["id"]


@pytest.mark.parametrize("reason", ["limit", "login", "network"])
def test_before_send_unusable_plus_falls_back_to_free_and_sends_once(tmp_path, reason):
    store, plus, free = accounts_fixture(tmp_path)
    folder = tmp_path / "job"
    folder.mkdir()
    attempts, sends = [], []

    def converter(account, _root, job, _cancel, _progress, **_options):
        attempts.append(account["id"])
        record = read_record(job, account["id"])
        if account["id"] == plus:
            record["error"] = reason
            write_record(job, record)
            raise BrowserProblem(reason, "Fixture unavailable")
        sends.append(account["id"])
        record.update(state="completed", url="https://chatgpt.com/c/fixture", error="")
        write_record(job, record)
        return {"path": "fixture.pptx", "url": record["url"]}

    result = convert_available(store.candidates(), store.root, folder, Event(), lambda _: None,
                               converter=converter, failed=store.login_error, retry_delays=())
    assert attempts == [plus, free] and sends == [free] and result["account_id"] == free
    assert store.preferred()["id"] == free
    assert read_record(folder, free)["state"] == "completed"
    assert store.get(plus)["ready"] == (reason != "login")
    assert bool(store.get(plus).get("quota_limited")) == (reason == "limit")


@pytest.mark.parametrize("state,url", [("submitting", ""), ("waiting", "https://chatgpt.com/c/fixture")])
def test_after_send_or_unknown_ack_never_switches_account(tmp_path, state, url):
    store, plus, _free = accounts_fixture(tmp_path)
    attempts = []

    def converter(account, _root, job, _cancel, _progress, **_options):
        attempts.append(account["id"])
        record = read_record(job, account["id"])
        record.update(state=state, url=url, error="limit")
        write_record(job, record)
        raise BrowserProblem("limit", "Fixture limit after send")

    with pytest.raises(BrowserProblem) as error:
        convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None,
                          converter=converter, failed=store.login_error)
    assert error.value.code == "limit" and attempts == [plus]
    assert read_record(tmp_path, plus)["state"] == state


def test_persisted_unsent_job_can_move_off_limited_account_without_relogin(tmp_path):
    store, plus, free = accounts_fixture(tmp_path)
    record = read_record(tmp_path, plus)
    record["error"] = "limit"
    write_record(tmp_path, record)
    store.login_error(plus, "limit", "Fixture limit")
    seen = []

    def converter(account, _root, job, *_args, **_options):
        seen.append(read_record(job, account["id"])["account_id"])
        return {"path": "fixture.pptx", "url": ""}

    convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None, converter=converter)
    assert seen == [free]
    assert BrowserAccounts(store.root.parent).get(plus)["quota_limited"]


def test_all_accounts_limited_stay_logged_in_and_do_not_claim_relogin_required(tmp_path):
    store, plus, free = accounts_fixture(tmp_path)
    for account in (plus, free):
        store.login_error(account, "limit", "Fixture limit")
    assert all(a["ready"] for a in store.data["accounts"])
    assert not store.candidates()
    with pytest.raises(ValueError, match="không cần đăng nhập lại"):
        store.preferred()
    store.observe(plus, "plus", identity={"name": "Fixture"})
    assert not store.candidates()  # Successful session check is not renewed quota.
    store.conversion_succeeded(plus)
    assert store.preferred()["id"] == plus
    store.remove(plus)  # Remaining limited account must not break deletion.
    assert len(store.data["accounts"]) == 1


def test_resume_keeps_free_even_when_plus_has_recovered(tmp_path):
    store, _plus, free = accounts_fixture(tmp_path)
    record = read_record(tmp_path, free)
    record.update(state="waiting", url="https://chatgpt.com/c/fixture")
    write_record(tmp_path, record)
    seen = []

    def converter(account, *_args, **_options):
        seen.append(account["id"])
        return {"path": "fixture.pptx", "url": record["url"]}

    convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None, converter=converter)
    assert seen == [free]


def test_cancelled_job_never_tries_another_account(tmp_path):
    store, _plus, _free = accounts_fixture(tmp_path)
    cancel = Event()
    cancel.set()
    with pytest.raises(BrowserProblem) as error:
        convert_available(store.candidates(), store.root, tmp_path, cancel, lambda _: None,
                          converter=lambda *_a, **_k: pytest.fail("Cancelled before browser opens"))
    assert error.value.code == "cancelled"


@pytest.mark.parametrize("state,url,reason", [("prepared", "", "network"),
    ("prepared", "", "upload"),
    ("prepared", "", "interface"),
    ("waiting", "https://chatgpt.com/c/fixture", "browser"),
    ("waiting", "https://chatgpt.com/c/fixture", "timeout"),
    ("waiting", "https://chatgpt.com/c/fixture", "download")])
def test_temporary_failure_recovers_automatically_on_same_account(tmp_path, state, url, reason):
    store, plus, _free = accounts_fixture(tmp_path)
    record = read_record(tmp_path, plus)
    record.update(state=state, url=url)
    write_record(tmp_path, record)
    attempts, failures, progress = [], [], []

    def converter(account, _root, folder, *_args, **_options):
        attempts.append(account["id"])
        job = read_record(folder, account["id"])
        if len(attempts) == 1:
            job["error"] = reason
            write_record(folder, job)
            raise BrowserProblem(reason, "Temporary fixture interruption")
        assert job["state"] == state and job["url"] == url
        return {"path": "fixture.pptx", "url": url}

    result = convert_available(store.candidates(), store.root, tmp_path, Event(), progress.append,
                               converter=converter, failed=lambda *args: failures.append(args), retry_delays=(0,))
    assert attempts == [plus, plus] and not failures and progress
    assert result["account_id"] == plus


@pytest.mark.parametrize("reason", ["upload", "interface"])
def test_preparation_recovery_is_bounded_and_never_switches_accounts(tmp_path, reason):
    store, plus, _free = accounts_fixture(tmp_path)
    attempts = []

    def converter(account, _root, folder, *_args, **_options):
        attempts.append(account["id"])
        write_record(folder, read_record(folder, account["id"]))
        raise BrowserProblem(reason, "Persistent preparation failure")

    with pytest.raises(BrowserProblem) as exc:
        convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None,
                          converter=converter, retry_delays=(0, 0))
    assert exc.value.code == reason and attempts == [plus, plus, plus]


@pytest.mark.parametrize("state,url", [("submitting", ""), ("waiting", "https://chatgpt.com/c/fixture")])
@pytest.mark.parametrize("reason", ["upload", "interface"])
def test_attachment_or_editor_failure_after_submit_never_reuploads(tmp_path, state, url, reason):
    store, plus, _free = accounts_fixture(tmp_path)
    attempts = []

    def converter(account, _root, folder, *_args, **_options):
        attempts.append(account["id"])
        record = read_record(folder, account["id"])
        record.update(state=state, url=url)
        write_record(folder, record)
        raise BrowserProblem(reason, "Already submitted")

    with pytest.raises(BrowserProblem):
        convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None,
                          converter=converter, retry_delays=(0, 0))
    assert attempts == [plus]


def test_unknown_send_reopens_only_same_account_to_find_receipt(tmp_path):
    store, plus, _free = accounts_fixture(tmp_path)
    attempts = []

    def converter(account, _root, folder, *_args, **_options):
        attempts.append(account["id"])
        record = read_record(folder, account["id"])
        record.update(state="submitting", error="browser")
        write_record(folder, record)
        raise BrowserProblem("browser", "Uncertain acknowledgement")

    with pytest.raises(BrowserProblem):
        convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None,
                          converter=converter, retry_delays=(0, 0))
    assert attempts == [plus, plus, plus]


def test_already_received_file_can_be_imported_without_session_or_quota(tmp_path):
    store, plus, _free = accounts_fixture(tmp_path)
    write_record(tmp_path, {"account_id": plus, "state": "completed", "url": "https://chatgpt.com/c/fixture", "followups": 0})
    store.login_error(plus, "limit", "Fixture limit")
    store.login_error(plus, "login", "Expired session")
    result = convert_available([store.get(plus)], store.root, tmp_path, Event(), lambda _: None,
        converter=lambda *_args, **_kwargs: {"path": "validated-local.pptx", "cached": True})
    assert result["cached"] and result["account_id"] == plus


def test_recovery_has_a_bound_and_cancellation_stops_before_reopen(tmp_path):
    store, plus, free = accounts_fixture(tmp_path)
    attempts = []

    def converter(account, _root, folder, *_args, **_options):
        attempts.append(account["id"])
        record = read_record(folder, account["id"])
        write_record(folder, record)
        if account["id"] == plus:
            raise BrowserProblem("network", "Persistent fixture failure")
        return {"path": "fixture.pptx", "url": ""}

    convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None,
                      converter=converter, retry_delays=(0, 0))
    assert attempts == [plus, plus, plus, free]
    cancel = Event()
    attempts.clear()
    with pytest.raises(BrowserProblem) as exc:
        convert_available(store.candidates(), store.root, tmp_path, cancel, lambda _: cancel.set(),
                          converter=converter, retry_delays=(1,))
    assert exc.value.code == "cancelled" and attempts == [plus]


def test_failed_result_transfer_retries_once_without_switching_or_restarting_on_launch(tmp_path):
    from app.browser_dispatch import startup_resume

    store, plus, _free = accounts_fixture(tmp_path)
    record = read_record(tmp_path, plus)
    record.update(state='waiting', url='https://chatgpt.com/c/fixture', auto_resume=True)
    write_record(tmp_path, record)
    calls = []

    def converter(account, _root, folder, *_args, **_options):
        calls.append(account['id'])
        record['error'] = 'file_transfer'
        write_record(folder, record)
        raise BrowserProblem('file_transfer', 'Known result stream interrupted')

    with pytest.raises(BrowserProblem):
        convert_available(store.candidates(), store.root, tmp_path, Event(), lambda _: None,
                          converter=converter, retry_delays=(0, 0, 0))
    assert calls == [plus, plus] and not startup_resume(tmp_path)
    store.login_error(plus, 'file_transfer', 'File transfer failed')
    assert store.get(plus)['ready'] and not store.get(plus).get('connection_retry_at')


@pytest.mark.parametrize("state,error,resumes", [("prepared", "upload", True),
    ("submitting", "receipt", True), ("waiting", "browser", True), ("completed", "", True),
    ("waiting", "verification", False), ("waiting", "limit", False), ("waiting", "no_file", False),
    ("waiting", "cancelled", False)])
def test_startup_recovery_requires_saved_authorization_and_obeys_stop(tmp_path, state, error, resumes):
    from app.browser_dispatch import startup_resume

    _store, plus, _free = accounts_fixture(tmp_path)
    record = read_record(tmp_path, plus)
    record.update(state=state, error=error, url="" if state in {"prepared", "submitting"} else "https://chatgpt.com/c/fixture")
    write_record(tmp_path, record)
    assert not startup_resume(tmp_path)
    record["auto_resume"] = True
    write_record(tmp_path, record)
    assert startup_resume(tmp_path) == resumes
    (tmp_path / "conversion-stopped").touch()
    assert not startup_resume(tmp_path)
    (tmp_path / "conversion-stopped").unlink()
    record["lesson_id"] = "already-saved"
    write_record(tmp_path, record)
    assert not startup_resume(tmp_path)


@pytest.mark.parametrize('flag',['wait_exhausted','recovery_exhausted'])
def test_exhausted_wait_or_recovery_never_restarts_on_retry_or_app_start(tmp_path,flag):
    from app.browser_dispatch import startup_resume

    store,plus,_=accounts_fixture(tmp_path)
    record=read_record(tmp_path,plus)
    record.update(state='waiting',url='https://chatgpt.com/c/fixture',auto_resume=True)
    write_record(tmp_path,record)
    calls=[]
    def converter(account,_root,folder,*args,**kw):
        calls.append(account['id'])
        record[flag]=True
        record['error']='timeout' if flag=='wait_exhausted' else 'network'
        write_record(folder,record)
        raise BrowserProblem(record['error'],'Already exhausted')
    with pytest.raises(BrowserProblem):
        convert_available(store.candidates(),store.root,tmp_path,Event(),lambda _:None,converter=converter,retry_delays=(0,0))
    assert calls==[plus] and not startup_resume(tmp_path)


def test_old_fifteen_minute_timeout_gets_one_startup_probe_but_hard_cap_does_not(tmp_path):
    from app.browser_dispatch import startup_resume

    _store, plus, _free = accounts_fixture(tmp_path)
    record = read_record(tmp_path, plus)
    record.update(state='waiting', url='https://chatgpt.com/c/fixture', error='timeout', auto_resume=True,
                  wait_exhausted=True, send_sha256='a'*64,
                  response_wait={'key':'a'*64, 'seconds':900.2, 'limit':900})
    write_record(tmp_path, record)
    assert startup_resume(tmp_path)
    record['timeout_probe_key'] = record['send_sha256']
    write_record(tmp_path, record)
    assert not startup_resume(tmp_path)
    record.pop('timeout_probe_key')
    record['response_wait'].update(seconds=3600, limit=3600)
    write_record(tmp_path, record)
    assert not startup_resume(tmp_path)
