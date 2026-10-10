import time
from threading import Event
from types import SimpleNamespace

import pytest

from app.browser_accounts import BrowserAccounts
from app.browser_health import health_due, quota_blocked, retry_delay


@pytest.fixture
def clock(monkeypatch):
    value = [100000.0]
    monkeypatch.setattr(time, "time", lambda: value[0])
    return value


def signed_account(tmp_path):
    store = BrowserAccounts(tmp_path)
    item = store.add("Teacher")
    store.observe(item["id"], "plus", identity={"name": "Teacher"})
    return store, item["id"]


def test_health_and_preflight_do_not_clear_quota_even_after_restart(tmp_path, clock):
    store, account_id = signed_account(tmp_path)
    store.login_error(account_id, "limit", "Usage limit. Try again in 2 hours.")
    deadline = store.get(account_id)["quota_retry_at"]
    clock[0] += 100
    store.observe(account_id, "plus", "Web model", identity={"name": "Teacher"})
    reloaded = BrowserAccounts(tmp_path)
    assert reloaded.get(account_id)["ready"]
    assert reloaded.get(account_id)["quota_retry_at"] == deadline
    assert quota_blocked(reloaded.get(account_id)) and not reloaded.candidates()
    assert not reloaded.due_accounts()
    with pytest.raises(ValueError, match="không cần đăng nhập lại"):
        reloaded.preferred()
    clock[0] = deadline + 1
    assert reloaded.candidates()[0]["id"] == account_id
    assert reloaded.get(account_id)["quota_limited"]  # Retry permission is not a balance reading.
    reloaded.conversion_succeeded(account_id)
    assert not BrowserAccounts(tmp_path).get(account_id)["quota_limited"]


def test_generic_quota_observation_never_shortens_known_cooldown(tmp_path, clock):
    store, account_id = signed_account(tmp_path)
    store.login_error(account_id, "limit", "Usage limit. Try again in 4 hours.")
    deadline = store.get(account_id)["quota_retry_at"]
    clock[0] += 100
    store.login_error(account_id, "limit", "Usage limit")
    assert store.get(account_id)["quota_retry_at"] == deadline
    assert store.get(account_id)["quota_reset_known"]


@pytest.mark.parametrize("code", ["network", "browser"])
def test_temporary_failure_preserves_session_and_defers_new_jobs(tmp_path, clock, code):
    store, account_id = signed_account(tmp_path)
    store.login_error(account_id, code, "Temporary connection problem")
    resumed = BrowserAccounts(tmp_path)
    assert resumed.get(account_id)["ready"] and not resumed.candidates()
    with pytest.raises(ValueError, match="không cần đăng nhập lại"):
        resumed.preferred()
    clock[0] += 301
    assert resumed.candidates() and resumed.due_accounts() == [account_id]
    resumed.observe(account_id, "free", identity={"name": "Teacher"})
    assert resumed.preferred()["plan"] == "free" and not resumed.due_accounts()


def test_busy_and_cancel_do_not_invalidate_or_extend_account_state(tmp_path, clock):
    store, account_id = signed_account(tmp_path)
    before = store.path.read_bytes()
    for code in ("busy", "cancelled"):
        store.login_error(account_id, code, "No work done")
    assert store.path.read_bytes() == before


def test_health_checks_stale_idle_profiles_but_never_auth_challenges(tmp_path, clock):
    store, account_id = signed_account(tmp_path)
    assert not health_due(store.get(account_id))
    clock[0] += 7201
    assert store.due_accounts() == [account_id]
    store.probe_started(account_id)
    assert not store.due_accounts()
    clock[0] += 7201
    store.login_error(account_id, "verification", "Human verification required")
    clock[0] += 86400
    assert not store.due_accounts()


@pytest.mark.parametrize("text,seconds", [("Try again in 2 hours", 7200), ("Try again after 15 minutes", 900),
    ("Thử lại sau 30 phút", 1800), ("Try again later", 0), ("The lesson lasts 2 hours", 0)])
def test_relative_quota_delay_requires_an_explicit_retry_hint(text, seconds):
    assert retry_delay(text) == seconds


def test_timer_checks_only_one_due_profile_and_yields_to_conversion(tmp_path, clock, monkeypatch):
    from PySide6.QtCore import QCoreApplication, QObject

    from app.browser_web_ui import WebBrowserAI

    application = QCoreApplication.instance() or QCoreApplication([])
    bridge = QObject()
    bridge.library = SimpleNamespace(directory=tmp_path)
    bridge.busy = False
    ui = WebBrowserAI(bridge)
    started = []
    try:
        for name in ("A", "B"):
            item = ui.store.add(name)
            ui.store.observe(item["id"], "free", identity={"name": name})
        clock[0] += 7201

        def start(account_id):
            ui.store.probe_started(account_id)
            started.append(account_id)
            ui.job = object()

        monkeypatch.setattr(ui, "_start_check", start)
        ui.refreshAccounts()
        ui.refreshAccounts()
        assert len(started) == 1
        ui.job = None
        bridge.busy = True
        ui.refreshAccounts()
        assert len(started) == 1
        bridge.busy = False
        ui.refreshAccounts()
        assert len(started) == 2 and started[0] != started[1]
        assert application is not None
    finally:
        ui.job = None
        ui.shutdown()


def test_conversion_cancels_background_probe_and_continues_without_relogin(tmp_path, monkeypatch):
    from PySide6.QtCore import QCoreApplication, QObject

    from app import browser_automation
    from app.browser_web_ui import WebBrowserAI

    application = QCoreApplication.instance() or QCoreApplication([])
    bridge = QObject()
    bridge.library = SimpleNamespace(directory=tmp_path)
    bridge.busy = False
    bridge.chatgptRequest = {"folder": str(tmp_path / "request")}
    continued, entered = [], Event()
    bridge.runBrowserAI = lambda: continued.append(bridge.chatgptRequest["folder"])

    def check(_account, _root, cancel, _progress):
        entered.set()
        assert cancel.wait(5)
        browser_automation.check_cancel(cancel)

    monkeypatch.setattr(browser_automation, "check_session", check)
    ui = WebBrowserAI(bridge)
    try:
        account = ui.store.add("Teacher")
        ui.store.observe(account["id"], "free", identity={"name": "Teacher"})
        ui.checkAccount(account["id"])
        assert entered.wait(5)
        assert ui.finishProbeBeforeConversion(bridge.chatgptRequest["folder"])
        deadline = time.monotonic() + 5
        while not continued and time.monotonic() < deadline:
            application.processEvents()
            time.sleep(.01)
        assert continued == [bridge.chatgptRequest["folder"]]
        assert not ui.loginBusy and ui.store.get(account["id"])["ready"]
        assert "last_error" not in ui.store.get(account["id"])
    finally:
        ui.shutdown()
