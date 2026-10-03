"""A system Edge login window with a BiliClass-only profile and lifetime.

No browser automation, shared profile access or cookie/token extraction.
Inference does not use this browser. Only the browser tree we create belongs
to our Windows job; closing it cannot close the user's other windows.
"""

import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from .browser_accounts import profile_lock


class LoginBrowserError(ValueError):
    pass


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
        self.profile = self.root / "sign-in-browser"
        self.process, self.lock = None, None

    def __enter__(self):
        if os.name != "nt":
            raise LoginBrowserError("Phiên đăng nhập riêng hiện hỗ trợ Windows và Microsoft Edge.")
        if self.profile.is_symlink() or not self.profile.resolve().is_relative_to(self.root):
            raise LoginBrowserError("Đường dẫn hồ sơ đăng nhập riêng không hợp lệ.")
        self.lock = profile_lock(self.root / "browser-lock", self.host_id)
        self.lock.__enter__()
        return self

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

    def __exit__(self, *args):
        try:
            if self.process:
                self.process.close()
                self.process = None
        finally:
            if self.lock:
                self.lock.__exit__(*args)
                self.lock = None
