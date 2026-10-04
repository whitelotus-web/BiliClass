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
