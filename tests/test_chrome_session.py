from pathlib import Path
from threading import Event

import pytest

from app.browser_accounts import BrowserAccounts
from app.chrome_session import ChromeSessionError, devtools_endpoint, open_chrome


@pytest.mark.parametrize("content", ["9222\nws://foreign.invalid/devtools/browser/a", "0\n/devtools/browser/a",
                                    "99999\n/devtools/browser/a", "9222\n/devtools/browser/a?token=x"])
def test_devtools_endpoint_never_uses_a_foreign_host_or_invalid_port(tmp_path, content):
    (tmp_path / "DevToolsActivePort").write_text(content)
    assert devtools_endpoint(tmp_path) is None
    (tmp_path / "DevToolsActivePort").write_text("9222\n/devtools/browser/fixture-123\n")
    assert devtools_endpoint(tmp_path) == "ws://127.0.0.1:9222/devtools/browser/fixture-123"


def test_cancel_before_start_never_launches_chrome(tmp_path, monkeypatch):
    from app import chrome_session

    accounts = BrowserAccounts(tmp_path)
    accounts.add("Fixture")
    cancel = Event()
    cancel.set()
    monkeypatch.setattr(chrome_session.subprocess, "Popen", lambda *_a, **_k: pytest.fail("Must not launch when cancelled"))
    with pytest.raises(ChromeSessionError, match="hủy"):
        open_chrome(None, accounts.get(), background=True, cancel=cancel)


def test_native_chrome_persists_only_its_own_fixture_session_and_closes_process(tmp_path):
    """Real Chrome, fake local session; no ChatGPT request or real credentials."""
    from playwright.sync_api import sync_playwright

    accounts = BrowserAccounts(tmp_path)
    first, second = accounts.add("First fixture"), accounts.add("Second fixture")
    url = "https://browser-session.fixture.test/"
    with sync_playwright() as playwright:
        context = open_chrome(playwright, accounts.get(first["id"]), background=True)
        process = context.process
        try:
            context.route("**/*", lambda r: r.fulfill(content_type="text/html", body="<title>Fixture</title>",
                          headers={"Set-Cookie": "fixture_session=fixture-only; Path=/; Max-Age=600; Secure; HttpOnly"}))
            page = context.pages[0]
            page.goto(url)
            page.evaluate("localStorage.setItem('fixture_marker', 'fixture-only')")
            import os
            if os.name == "nt":
                import win32gui
                import win32process

                owned = []
                win32gui.EnumWindows(lambda hwnd, _: owned.append(hwnd)
                    if win32process.GetWindowThreadProcessId(hwnd)[1] == process.pid
                    and win32gui.GetClassName(hwnd) == "Chrome_WidgetWin_1" else None, None)
                assert owned and all(not win32gui.IsWindowVisible(hwnd) for hwnd in owned)
        finally:
            context.close()
        assert process.poll() is not None

        seen = []
        for item, expected in ((first, "fixture-only"), (second, None)):
            context = open_chrome(playwright, accounts.get(item["id"]), background=True)
            process = context.process
            try:
                def route(request):
                    seen.append((item["id"], request.request.headers.get("cookie", "")))
                    request.fulfill(content_type="text/html", body="<title>Fixture</title>")
                context.route("**/*", route)
                page = context.pages[0]
                page.goto(url)
                assert page.evaluate("localStorage.getItem('fixture_marker')") == expected
                assert Path(accounts.get(item["id"])["profile"]).name == "chrome"
            finally:
                context.close()
            assert process.poll() is not None
        assert any(account == first["id"] and "fixture_session=fixture-only" in cookie for account, cookie in seen)
        assert all(not cookie for account, cookie in seen if account == second["id"])


def test_plain_chrome_login_saves_session_without_debugging_and_closes_only_owned_window(tmp_path, monkeypatch):
    """Real native Chrome + localhost fixture, never a real sign-in or token."""
    import os
    import time
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    from playwright.sync_api import sync_playwright

    from app import chrome_session

    loaded, requests, launched = Event(), [], []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.path, self.headers.get("Cookie", "")))
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            if self.path == "/sign-in":
                self.send_header("Set-Cookie", "fixture_saved=fixture-only; Path=/; Max-Age=600; HttpOnly")
            self.end_headers()
            self.wfile.write(b"<title>BiliClass local fixture</title><h1>Fixture</h1>")
            if self.path == "/sign-in":
                loaded.set()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    address = f"http://127.0.0.1:{server.server_port}"
    accounts = BrowserAccounts(tmp_path)
    first, other = accounts.add("Plain fixture"), accounts.add("Unrelated fixture")
    original_popen = chrome_session.subprocess.Popen

    def start_minimized(arguments, **options):
        launched.append(arguments)
        if os.name == "nt":
            startup = chrome_session.subprocess.STARTUPINFO()
            startup.dwFlags |= chrome_session.subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = 6  # The test must not interrupt the human login window.
            options["startupinfo"] = startup
        return original_popen(arguments, **options)

    try:
        with sync_playwright() as playwright:
            unrelated = open_chrome(playwright, accounts.get(other["id"]), background=True)
            try:
                # This second process must survive closing the native fixture.
                unrelated.pages[0].goto(address + "/other")
                monkeypatch.setattr(chrome_session.subprocess, "Popen", start_minimized)
                plain = chrome_session.PlainChromeLogin(accounts.get(first["id"]), address + "/sign-in")
                try:
                    assert loaded.wait(15), "Native Chrome did not load the local fixture"
                    assert plain.running()
                    assert len(launched) == 1
                    assert not any("remote-debugging" in arg or "headless" in arg or "automation" in arg for arg in launched[0])
                    if os.name == "nt":
                        import win32gui
                        import win32process

                        windows = []
                        deadline = time.monotonic() + 5
                        while not windows and time.monotonic() < deadline:
                            def find_window(hwnd, _):
                                if win32gui.IsWindowVisible(hwnd) and win32process.GetWindowThreadProcessId(hwnd)[1] == plain.process.pid:
                                    windows.append(hwnd)
                            win32gui.EnumWindows(find_window, None)
                            if not windows:
                                time.sleep(.05)
                        assert windows, "Native fixture has no owned window to close"
                    plain.finish()
                    assert not plain.running()
                    assert unrelated.process.poll() is None
                    assert unrelated.pages[0].evaluate("1 + 1") == 2
                finally:
                    plain.close()

                monkeypatch.setattr(chrome_session.subprocess, "Popen", original_popen)
                verified = open_chrome(playwright, accounts.get(first["id"]), background=True)
                try:
                    verified.pages[0].goto(address + "/check")
                    assert any(path == "/check" and "fixture_saved=fixture-only" in cookie for path, cookie in requests)
                    assert not accounts.get(first["id"])["ready"], "A fixture cookie must never mark a ChatGPT account ready"
                finally:
                    verified.close()
            finally:
                unrelated.close()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)
