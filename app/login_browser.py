"""A system Edge login window with a BiliClass-only profile and lifetime.

No browser automation, shared profile access or cookie/token extraction.
Inference does not use this browser. Only the browser tree we create belongs
to our Windows job; closing it cannot close the user's other windows.
"""

import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from .browser_accounts import profile_lock


class LoginBrowserError(ValueError):
    pass


def login_window_status(titles):
    """Classify known top-level titles only; never read page forms or cookies."""
    values = [title.casefold().replace("’", "'").strip() for title in titles]
    if any(value.startswith("this account can't access this app") and value.endswith("openai") for value in values):
        return "workspace_denied"
    if any(value.startswith("authentication error") and value.endswith("openai") for value in values):
        return "authentication_error"
    if not values or all(not value or value in {"microsoft edge", "about:blank"}
                         or value.startswith("auth.openai.com") for value in values):
        return "loading"
    return "waiting"


def edge_executable():
    for variable in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
        root = os.environ.get(variable)
        if root:
            candidate = Path(root) / "Microsoft/Edge/Application/msedge.exe"
            if candidate.is_file():
                return candidate
    raise LoginBrowserError("Cần Microsoft Edge để mở phiên đăng nhập riêng của BiliClass.")


class OwnedProcess:
    """Suspended startup ensures every child belongs to our kill-on-close job."""

    def __init__(self, executable, arguments):
        import win32con
        import win32job
        import win32process

        self.job, self.process = None, None
        thread = None
        try:
            self.job = win32job.CreateJobObject(None, "")
            limits = win32job.QueryInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation)
            limits["BasicLimitInformation"]["LimitFlags"] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            win32job.SetInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation, limits)
            self.process, thread, self.pid, _ = win32process.CreateProcess(
                str(executable), subprocess.list2cmdline([str(executable), *arguments]),
                None, None, False, win32con.CREATE_SUSPENDED | win32con.CREATE_NO_WINDOW,
                None, None, win32process.STARTUPINFO(),
            )
            win32job.AssignProcessToJobObject(self.job, self.process)
            win32process.ResumeThread(thread)
        except Exception:
            if self.process:
                win32process.TerminateProcess(self.process, 1)
            self.close()
            raise LoginBrowserError("Chưa mở được phiên đăng nhập riêng. Đóng phiên BiliClass cũ và thử lại.") from None
        finally:
            if thread:
                thread.Close()

    def running(self):
        import win32job

        return bool(self.job and win32job.QueryInformationJobObject(
            self.job, win32job.JobObjectBasicAccountingInformation)["ActiveProcesses"])

    def window_titles(self):
        import win32gui
        import win32job
        import win32process

        if not self.job:
            return []
        processes = set(win32job.QueryInformationJobObject(self.job, win32job.JobObjectBasicProcessIdList))
        titles = []

        def owned_window(hwnd, _):
            try:
                if win32gui.IsWindowVisible(hwnd) and win32process.GetWindowThreadProcessId(hwnd)[1] in processes:
                    titles.append(win32gui.GetWindowText(hwnd))
            except Exception:
                pass  # A window may disappear during enumeration.
        win32gui.EnumWindows(owned_window, None)
        return titles

    def close(self):
        import win32event

        if self.job:
            self.job.Close()
            self.job = None
        if self.process:
            win32event.WaitForSingleObject(self.process, 5000)
            self.process.Close()
            self.process = None


class PrivateLoginBrowser:
    def __init__(self, accounts):
        self.root = accounts.root
        self.host_id = accounts.host_id[9:]
        # Browser caches on the library drive made source runs unnecessarily slow.
        # Keep them on the Windows local app-data drive, keyed by this installation.
        local = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        self.profile_root = (local / "BiliClass/sign-in-browsers").resolve()
        self.profile = self.profile_root / self.host_id
        self.process, self.lock = None, None

    def __enter__(self):
        if os.name != "nt":
            raise LoginBrowserError("Phiên đăng nhập riêng hiện hỗ trợ Windows và Microsoft Edge.")
        if self.profile.is_symlink() or not self.profile.resolve().is_relative_to(self.profile_root):
            raise LoginBrowserError("Đường dẫn hồ sơ đăng nhập riêng không hợp lệ.")
        self.lock = profile_lock(self.root / "browser-lock", self.host_id)
        self.lock.__enter__()
        try:
            self._select_profile()
            return self
        except Exception:
            self.lock.__exit__(None, None, None)
            self.lock = None
            raise

    def _select_profile(self):
        from .chatgpt_auth import atomic_json

        record_path = self.root / "sign-in-browser.json"
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.is_file() else {}
        profile_id = record.get("profile_id", "")
        if profile_id and str(UUID(profile_id)) != profile_id:
            raise LoginBrowserError("Định danh hồ sơ đăng nhập không hợp lệ.")
        code = self._last_error_code()
        if code in {"invalid_grant", "invalid_state", "browser_authentication_error"}:
            # Preserve the previous profile. Only this app's login browser gets
            # a fresh folder; host/client registrations and credentials stay put.
            profile_id = str(uuid4())
            atomic_json(record_path, {"profile_id": profile_id})
        target = self.profile_root / (self.host_id + "-" + profile_id if profile_id else self.host_id)
        if target.is_symlink() or not target.resolve().is_relative_to(self.profile_root):
            raise LoginBrowserError("Đường dẫn hồ sơ đăng nhập riêng không hợp lệ.")
        self.profile = target

    def _last_error_code(self):
        # Read only our public error metadata, never a browser cookie database.
        path = self.root / "accounts.json"
        if not path.is_file():
            return ""
        return json.loads(path.read_text(encoding="utf-8")).get("last_error", {}).get("code", "")

    def open(self, url):
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "auth.openai.com" or parsed.fragment:
            raise LoginBrowserError("Địa chỉ đăng nhập ChatGPT không hợp lệ.")
        self.profile.mkdir(parents=True, exist_ok=True)
        self.process = OwnedProcess(edge_executable(), [
            "--user-data-dir=" + str(self.profile), "--app=" + url,
            "--no-first-run", "--no-default-browser-check", "--disable-background-mode",
            "--disable-sync", "--disable-extensions",
        ])
        return True

    def running(self):
        return bool(self.process and self.process.running())

    def status(self):
        return login_window_status(self.process.window_titles()) if self.process else "loading"

    def __exit__(self, *args):
        try:
            if self.process:
                self.process.close()
                self.process = None
        finally:
            if self.lock:
                self.lock.__exit__(*args)
                self.lock = None
