import json
import os
import subprocess
import sys
import time

import psutil
import pytest

from app.chatgpt_auth import PlanAccounts
from app.login_browser import LoginBrowserError, OwnedProcess, PrivateLoginBrowser, login_window_status


@pytest.mark.skipif(os.name != "nt", reason="Windows job and Edge profile")
def test_job_closes_its_tree_and_preserves_unrelated_process(tmp_path):
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                                 creationflags=subprocess.CREATE_NO_WINDOW)
    child_record = tmp_path / "child.txt"
    code = ("import subprocess,sys,time; from pathlib import Path; "
            "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],creationflags=0x08000000); "
            "Path(sys.argv[1]).write_text(str(p.pid)); time.sleep(30)")
    owned = None
    try:
        owned = OwnedProcess(sys.executable, ["-c", code, str(child_record)])
        deadline = time.monotonic() + 10
        while not child_record.exists() and time.monotonic() < deadline:
            time.sleep(.05)
        assert child_record.exists() and owned.running()
        assert owned.window_titles() == []
        child_pid = int(child_record.read_text())
        assert psutil.pid_exists(child_pid)
        owned.close()
        deadline = time.monotonic() + 5
        while psutil.pid_exists(child_pid) and time.monotonic() < deadline:
            time.sleep(.05)
        assert not psutil.pid_exists(child_pid)
        assert unrelated.poll() is None
        assert not owned.running()
    finally:
        if owned:
            owned.close()
        unrelated.terminate()
        unrelated.wait(5)


@pytest.mark.skipif(os.name != "nt", reason="Windows Edge profile")
def test_login_profile_is_owned_and_rejects_foreign_login_url(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local-app-data"))
    accounts = PlanAccounts(tmp_path)
    with PrivateLoginBrowser(accounts) as browser:
        assert browser.profile.is_relative_to(tmp_path / "local-app-data/BiliClass/sign-in-browsers")
        assert browser.profile.name == accounts.host_id[9:]
        with pytest.raises(LoginBrowserError, match="không hợp lệ"):
            browser.open("https://example.test/login?code=private")
        assert not browser.running()
    assert not accounts.data["accounts"]


@pytest.mark.parametrize("titles,status", [
    ([], "loading"), (["auth.openai.com/api/accounts/authorize"], "loading"),
    (["This account can't access this app - OpenAI"], "workspace_denied"),
    (["This account can’t access this app - OpenAI"], "workspace_denied"),
    (["Authentication Error - OpenAI"], "authentication_error"),
    (["Log in - OpenAI"], "waiting"), (["Select a workspace - OpenAI"], "waiting"),
])
def test_known_browser_window_titles(titles, status):
    assert login_window_status(titles) == status


@pytest.mark.skipif(os.name != "nt", reason="Windows Edge profile")
@pytest.mark.parametrize("code", ["invalid_grant", "invalid_state", "browser_authentication_error"])
def test_failed_session_uses_fresh_profile_without_erasing_host_or_registration(tmp_path, monkeypatch, code):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local-app-data"))
    accounts = PlanAccounts(tmp_path)
    accounts.save_registration("oaiapp_kept")
    original = PrivateLoginBrowser(accounts).profile
    original.mkdir(parents=True)
    sentinel = original / "do-not-delete.txt"
    sentinel.write_text("previous profile")
    accounts.data["last_error"] = {"code": code}
    accounts.save()
    host = accounts.host_id
    with PrivateLoginBrowser(accounts) as browser:
        assert browser.profile != original and browser.profile.is_relative_to(browser.profile_root)
        selected = browser.profile
    assert sentinel.read_text() == "previous profile"
    assert accounts.host_id == host
    assert accounts.registration(resume_pending=True)["client_id"] == "oaiapp_kept"
    # With a successful/cleared error, reuse this app's selected fresh profile.
    accounts.data["last_error"] = {}
    accounts.save()
    with PrivateLoginBrowser(accounts) as browser:
        assert browser.profile == selected
    assert json.loads((accounts.root / "sign-in-browser.json").read_text())["profile_id"] in selected.name
