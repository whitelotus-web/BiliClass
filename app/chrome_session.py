"""Start only BiliClass-owned Chrome profiles and attach via local DevTools.

Uses Chrome's supported debugging interface. No personal profile, imported
cookies, browser fingerprint changes or verification bypass.
"""

import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from threading import Event


class ChromeSessionError(ValueError):
    pass


def chrome_executable():
    candidates = []
    if os.name == "nt":
        for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(variable)
            if base:
                candidates.append(Path(base) / "Google/Chrome/Application/chrome.exe")
    else:
        for name in ("google-chrome", "google-chrome-stable"):
            found = shutil.which(name)
            if found:
                candidates.append(Path(found))
        candidates.append(Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ChromeSessionError("Chưa tìm thấy Google Chrome. Cài hoặc cập nhật Chrome rồi bấm Đăng nhập lại.")


def devtools_endpoint(profile):
    """Read a fresh endpoint from this process's isolated profile only."""
    try:
        lines = (profile / "DevToolsActivePort").read_text(encoding="utf-8").splitlines()
        if len(lines) != 2 or not lines[0].isdigit() or not 1 <= int(lines[0]) <= 65535:
            return None
        if not re.fullmatch(r"/devtools/browser/[a-zA-Z0-9-]+", lines[1]):
            return None
        return f"ws://127.0.0.1:{int(lines[0])}{lines[1]}"
    except (OSError, UnicodeError):
        return None


class ChromeSession:
    """Context-shaped owner of one Chrome process, including graceful shutdown."""

    def __init__(self, browser, process):
        self.browser = browser
        self.process = process
        self.context = browser.contexts[0]
        self.closed = False

    def __getattr__(self, name):
        return getattr(self.context, name)

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            # Closing a CDP connection alone leaves native Chrome running.
            # Ask Chrome to flush its persistent profile and exit first.
            self.browser.new_browser_cdp_session().send("Browser.close")
        except Exception:
            pass
        try:
            self.browser.close()
        except Exception:
            pass
        stop_process(self.process)


def stop_process(process):
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)


def open_chrome(playwright, account, *, background, cancel=None, timeout=30):
    profile = Path(account["profile"])
    if account.get("channel") != "chrome" or profile.name != "chrome":
        raise ChromeSessionError("Hồ sơ Browser AI cần chuyển sang Chrome. Mở lại BiliClass rồi đăng nhập.")
    profile.mkdir(parents=True, exist_ok=True)
    # A stale file must never attach us to another process after a crash.
    (profile / "DevToolsActivePort").unlink(missing_ok=True)
    cancel = cancel or Event()
    if cancel.is_set():
        raise ChromeSessionError("Đã hủy mở Chrome.")
    arguments = [str(chrome_executable()), f"--user-data-dir={profile}",
                 "--remote-debugging-address=127.0.0.1", "--remote-debugging-port=0",
                 "--no-first-run", "--no-default-browser-check", "--disable-session-crashed-bubble",
                 "--window-size=1360,900"]
    arguments.append("about:blank")
    startup = None
    if os.name == "nt" and background:
        # Keep the same browser mode as sign-in. Work is minimized rather than
        # restarting the saved account in a different headless environment.
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 6  # SW_MINIMIZE
    process = subprocess.Popen(arguments, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               startupinfo=startup,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    browser = None
    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not cancel.is_set():
            if process.poll() is not None:
                raise ChromeSessionError("Chrome riêng đã đóng hoặc hồ sơ đang được sử dụng. Đóng phiên đó rồi thử lại.")
            endpoint = devtools_endpoint(profile)
            if endpoint:
                browser = playwright.chromium.connect_over_cdp(endpoint, timeout=10000)
                if not browser.contexts:
                    raise ChromeSessionError("Chrome chưa tạo được hồ sơ riêng. Đóng cửa sổ đó và thử lại.")
                context = ChromeSession(browser, process)
                context.set_default_timeout(5000)
                if background and context.pages:
                    try:
                        session = context.new_cdp_session(context.pages[0])
                        window = session.send("Browser.getWindowForTarget")
                        session.send("Browser.setWindowBounds", {"windowId": window["windowId"],
                                     "bounds": {"windowState": "minimized"}})
                        session.detach()
                    except Exception:
                        pass  # Window managers may not support minimization.
                return context
            cancel.wait(.1)
        raise ChromeSessionError("Đã hủy mở Chrome." if cancel.is_set()
                                 else "Chrome chưa khởi động xong. Kiểm tra Chrome rồi thử lại.")
    except Exception:
        try:
            if browser:
                browser.new_browser_cdp_session().send("Browser.close")
        except Exception:
            pass
        try:
            if browser:
                browser.close()
        except Exception:
            pass
        finally:
            stop_process(process)
        raise
