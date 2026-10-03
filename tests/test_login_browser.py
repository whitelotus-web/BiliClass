import os
import subprocess
import sys
import time

import psutil
import pytest

from app.chatgpt_auth import PlanAccounts
from app.login_browser import LoginBrowserError, OwnedProcess, PrivateLoginBrowser


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
def test_login_profile_is_owned_and_rejects_foreign_login_url(tmp_path):
    accounts = PlanAccounts(tmp_path)
    with PrivateLoginBrowser(accounts) as browser:
        assert browser.profile.parent == accounts.root
        with pytest.raises(LoginBrowserError, match="không hợp lệ"):
            browser.open("https://example.test/login?code=private")
        assert not browser.running()
    assert not accounts.data["accounts"]
