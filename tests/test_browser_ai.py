import json
from pathlib import Path
from threading import Event

import pytest

from app.browser_accounts import BrowserAccounts, ProfileBusy, profile_lock
from app.browser_audio import prepare_narration
from app.browser_automation import BrowserProblem, conversation_url, read_record, write_record


def test_profiles_are_separate_persisted_and_deleted_with_session_data(tmp_path):
    accounts = BrowserAccounts(tmp_path)
    first = accounts.add("Cô A", "msedge")
    second = accounts.add("Thầy B", "chrome")
    assert accounts.get()["id"] == first["id"]
    accounts.select(second["id"])
    accounts.options(False, True)
    resumed = BrowserAccounts(tmp_path)
    assert resumed.get()["id"] == second["id"] and not resumed.data["automatic"]
    assert resumed.profile(first["id"]) != resumed.profile(second["id"])
    (resumed.profile(first["id"]) / "session-marker.txt").write_text("fixture only")
    with profile_lock(resumed.root, first["id"]):
        with pytest.raises(ProfileBusy):
            resumed.remove(first["id"])
    resumed.remove(first["id"])
    assert not resumed.profile(first["id"]).exists()
    assert resumed.get()["id"] == second["id"]
    resumed.remove(second["id"])
    with pytest.raises(ValueError, match="Thêm và chọn"):
        resumed.get()
    assert resumed.data["active"] == ""
    with pytest.raises(ValueError):
        resumed.profile("../../elsewhere")


def test_job_keeps_conversation_and_refuses_another_account_or_foreign_url(tmp_path):
    job = read_record(tmp_path, "account-a")
    job.update(state="waiting", url="https://chatgpt.com/c/fixture-123")
    write_record(tmp_path, job)
    assert read_record(tmp_path, "account-a") == job
    with pytest.raises(BrowserProblem, match="tài khoản khác"):
        read_record(tmp_path, "account-b")
    job["url"] = "https://chatgpt.com.evil.invalid/c/fixture-123"
    write_record(tmp_path, job)
    with pytest.raises(BrowserProblem, match="không hợp lệ"):
        read_record(tmp_path, "account-a")
    assert conversation_url("https://chatgpt.com/c/fixture-123")
    assert not conversation_url("https://chatgpt.com/c/fixture-123?token=secret")


def test_draft_audio_never_approves_or_plays_and_does_not_discard_other_voice(monkeypatch, tmp_path):
    from app import speech

    calls = []
    units = [{"vi": "Một câu tiếng Việt.", "en": "One English sentence.", "approved": False},
             {"vi": "", "en": "x" * 5001, "approved": False}]

    def synthesize(text, voice, rate, directory):
        calls.append((text, voice, rate, directory))
        if voice == "unavailable":
            raise ValueError("Missing model")

    monkeypatch.setattr(speech, "synthesize", synthesize)
    monkeypatch.setattr(speech, "play", lambda *_: pytest.fail("Draft audio must not play"))
    result = prepare_narration({"profile": {"units": units}}, {"vi": "unavailable", "en": "good", "rate": 0},
                               tmp_path, Event(), lambda _: None)
    assert result == {"complete": 1, "skipped": 1, "failed": 1, "total": 3}
    assert len(calls) == 2 and not any(u["approved"] for u in units)
    cancelled = Event()
    cancelled.set()
    result = prepare_narration({"profile": {"units": units}}, {"vi": "good", "en": "good", "rate": 0},
                               tmp_path, cancelled, lambda _: None)
    assert result["complete"] == 0 and len(calls) == 2


def test_profiles_do_not_enter_library_backup(tmp_path):
    from app.library import Library
    from app.storage import backup_library

    library = Library(tmp_path / "library")
    try:
        accounts = BrowserAccounts(library.directory)
        item = accounts.add("Cô A", "msedge")
        (accounts.profile(item["id"]) / "session-marker").write_text("Not a credential")
        path = backup_library(library.directory, tmp_path / "backup.bcbackup")
        import zipfile
        with zipfile.ZipFile(path) as archive:
            assert not any("browser_ai" in name or "session-marker" in name for name in archive.namelist())
    finally:
        library.close()


# A real Edge browser against a routed fixture: no ChatGPT account or uploads to the Internet.
FIXTURE = """<!DOCTYPE html><html><head><title>Browser AI fixture</title></head><body>
<button data-testid="accounts-profile-button">Fixture account</button>
<textarea id="prompt-textarea"></textarea><input type="file" multiple id="files"><div id="attached"></div>
<button data-testid="send-button" id="send">Send</button><div id="messages"></div>
<script>
function result() { document.querySelector('#messages').innerHTML = '<div data-message-author-role="assistant"><a href="/backend-api/files/result.pptx">bai-giang-song-ngu.pptx</a></div>'; }
if (location.pathname.startsWith('/c/')) result();
document.querySelector('#files').onchange = (e) => {document.querySelector('#attached').replaceChildren(...[...e.target.files].map(f => {const n=document.createElement('span');n.textContent=f.name;return n;}));};
document.querySelector('#send').onclick = () => {console.log('FIXTURE-SEND:' + JSON.stringify({prompt:document.querySelector('#prompt-textarea').value,files:[...document.querySelector('#files').files].map(f=>f.name)}));history.pushState({},'', '/c/fixture-123');result();};
</script></body></html>"""


@pytest.fixture
def browser_fixture(monkeypatch, tmp_path):
    from pptx import Presentation
    from pptx.util import Inches

    from app import browser_automation as adapter
    from app.chatgpt_handoff import prepare_request

    source = tmp_path / "source.pptx"
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    slide.shapes.add_textbox(Inches(.5), Inches(.5), Inches(8), Inches(2)).text = "Một slide để kiểm tra"
    slide.notes_slide.notes_text_frame.text = "VI: Một câu tiếng Việt.\nEN: One English sentence.\nCHECK: Kiểm tra số liệu."
    deck.save(source)
    accounts = BrowserAccounts(tmp_path / "library")
    accounts.add("Fixture account", "msedge")
    config = {"title": "Fixture", "subject": "Toán", "education_level": "THPT", "grade": "11",
              "level": 2, "layout": "split_view", "preset": "standard", "style": "source", "mode": "level"}
    request = prepare_request(tmp_path / "library", config, source)
    original = adapter.open_context
    captured = {"sends": [], "contexts": 0, "challenge": False, "download_failure": False}

    def opening(playwright, account, *, headless):
        captured["contexts"] += 1
        context = original(playwright, account, headless=headless)

        def route(req):
            if "/backend-api/files/result.pptx" in req.request.url:
                if captured["download_failure"]:
                    req.fulfill(status=500, content_type="text/plain", body="Fixture download failed")
                else:
                    req.fulfill(body=source.read_bytes(), headers={"Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                                                 "Content-Disposition": 'attachment; filename="fixture.pptx"'})
            else:
                content = '<html><head><title>Just a moment...</title></head><body id="challenge-stage">Verify</body></html>' if captured["challenge"] else FIXTURE
                req.fulfill(status=403 if captured["challenge"] else 200, content_type="text/html", body=content)

        context.route("**/*", route)
        for page in context.pages:
            page.on("console", lambda msg: captured["sends"].append(json.loads(msg.text.split(":", 1)[1]))
                    if msg.text.startswith("FIXTURE-SEND:") else None)
        return context

    monkeypatch.setattr(adapter, "open_context", opening)
    return adapter, accounts, request, captured, source


def test_real_browser_upload_download_and_repeat_does_not_send_twice(browser_fixture):
    adapter, accounts, request, captured, source = browser_fixture
    result = adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None, timeout=10)
    assert Path(result["path"]).read_bytes() == source.read_bytes()
    assert len(captured["sends"]) == 1
    assert captured["sends"][0] == {"files": ["tai-lieu-goc.pptx"], "prompt": request["prompt"]}
    assert "Hai cột" in captured["sends"][0]["prompt"]
    assert read_record(request["folder"], accounts.get()["id"])["state"] == "completed"
    assert adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None) == result
    assert len(captured["sends"]) == 1 and captured["contexts"] == 1
    inspection = adapter.inspect_returned_deck(result["path"])
    assert inspection["profile"]["units"][0]["en"] == "One English sentence."
    Path(result["path"]).write_bytes(b"altered")
    with pytest.raises(BrowserProblem, match="bị thay đổi"):
        adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None)
    assert len(captured["sends"]) == 1


def test_challenge_stops_before_upload_and_can_retry_same_request(browser_fixture):
    adapter, accounts, request, captured, _ = browser_fixture
    captured["challenge"] = True
    with pytest.raises(BrowserProblem, match="xác minh"):
        adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None, timeout=10)
    record = read_record(request["folder"], accounts.get()["id"])
    assert record["state"] == "prepared" and record["error"] == "verification" and not captured["sends"]
    captured["challenge"] = False
    adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None, timeout=10)
    assert len(captured["sends"]) == 1


def test_resume_download_uses_conversation_without_resending_input(browser_fixture):
    adapter, accounts, request, captured, source = browser_fixture
    record = read_record(request["folder"], accounts.get()["id"])
    record.update(state="waiting", url="https://chatgpt.com/c/fixture-123")
    write_record(request["folder"], record)
    result = adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None, timeout=10)
    assert Path(result["path"]).read_bytes() == source.read_bytes() and not captured["sends"]


def test_uncertain_send_is_not_repeated(browser_fixture):
    adapter, accounts, request, captured, _ = browser_fixture
    record = read_record(request["folder"], accounts.get()["id"])
    record["state"] = "submitting"
    write_record(request["folder"], record)
    with pytest.raises(BrowserProblem, match="không gửi trùng"):
        adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None, timeout=10)
    assert not captured["sends"]


def test_active_profile_cannot_overwrite_another_running_job(browser_fixture):
    adapter, accounts, request, captured, _ = browser_fixture
    record = read_record(request["folder"], accounts.get()["id"])
    record.update(state="waiting", url="https://chatgpt.com/c/fixture-123")
    write_record(request["folder"], record)
    with profile_lock(accounts.root, accounts.get()["id"]):
        with pytest.raises(ProfileBusy):
            adapter.convert(accounts.get(), accounts.root, request["folder"], Event(), lambda _: None)
    assert read_record(request["folder"], accounts.get()["id"]) == record and not captured["contexts"]
