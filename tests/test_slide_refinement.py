import json
from contextlib import nullcontext
from pathlib import Path
from threading import Event
from types import SimpleNamespace

import pytest

from app import browser_automation as web
from app.chatgpt_handoff import make_prompt


def test_saved_lesson_repair_opens_same_chat_and_selects_web_model_before_refining(tmp_path, monkeypatch):
    from app import browser_capabilities as capabilities
    from app.slide_refinement import repair_existing

    original = tmp_path / "original"
    original.mkdir()
    (original / "source.pptx").write_bytes(b"source")
    pending = tmp_path / "received.pptx"
    pending.write_bytes(b"received")
    request = {"config": {"source_file": "source.pptx", "style": "source", "conversion_format": "parallel_columns"}}
    parent = {"account_id": "same", "state": "completed", "url": "https://chatgpt.com/c/same", "followups": 0}
    web.write_record(original, parent)
    monkeypatch.setattr("app.chatgpt_handoff.load_request", lambda _: request)
    monkeypatch.setattr(web, "inspect_returned_deck", lambda *a: {"slide_quality": quality()})
    monkeypatch.setattr("app.browser_accounts.profile_lock", lambda *a: nullcontext())
    monkeypatch.setattr("playwright.sync_api.sync_playwright", lambda: nullcontext("driver"))
    calls = []
    page = SimpleNamespace(set_default_timeout=lambda _: None)
    context = SimpleNamespace(pages=[page], close=lambda: calls.append("closed"))
    monkeypatch.setattr(web, "open_context", lambda *a, **kw: context)
    monkeypatch.setattr(web, "navigate", lambda p, url, cancel: calls.append(url))
    monkeypatch.setattr(web, "require_account", lambda *a: None)
    monkeypatch.setattr(capabilities, "select_best_model", lambda p: calls.append("model") or "Thinking")
    monkeypatch.setattr(capabilities, "select_reasoning", lambda p: calls.append("reasoning") or "Extended")
    monkeypatch.setattr("app.slide_refinement.refine", lambda *a: calls.append("refine"))
    result = repair_existing({"id": "same", "ready": True}, tmp_path, original, pending, tmp_path / "data",
                             "lesson", 1, Event(), lambda _: None)
    assert not result.get("message")
    assert calls == [parent["url"], "model", "reasoning", "refine", "closed"]


@pytest.fixture(autouse=True)
def isolated_local_check(monkeypatch):
    def checked(path, folder, **kwargs):
        data = web.inspect_returned_deck(Path(path))
        return {"path": str(path), "inspection": data, "changes": []}
    monkeypatch.setattr("app.slide_refinement.repair_and_inspect", checked)


def quality(failed=True):
    return {"sha256": "a"*64, "slides": [{"slide": 1, "render_image": "",
        "issues": [{"code": "text_overflow", "severity": "FAIL" if failed else "CHECK"}]}]}


def test_refinement_uses_same_conversation_once_and_keeps_original_draft(tmp_path, monkeypatch):
    pending = tmp_path / "result.pptx"
    pending.write_bytes(b"original")
    request = {"config": {"source_file": "source.pptx", "style": "source", "conversion_format": "parallel_columns"}}
    (tmp_path / "source.pptx").write_bytes(b"source")
    monkeypatch.setattr(web, "inspect_returned_deck", lambda *args: {"slide_quality": quality(Path(args[0]).read_bytes() == b"original")})
    monkeypatch.setattr("app.slide_quality.render_quality", lambda p, d, q, *a: q)
    recorded, sends = [], []
    monkeypatch.setattr(web, "write_record", lambda folder, rec: recorded.append(dict(rec)))
    monkeypatch.setattr(web, "submit", lambda page, folder, rec, prompt, cancel, **kw: sends.append((page, prompt, kw["files"])))
    monkeypatch.setattr(web, "wait_result", lambda *args: "link")

    class Download:
        suggested_filename = "fixed.pptx"

        def path(self):
            return str(pending)

        def save_as(self, path):
            Path(path).write_bytes(b"corrected")

    monkeypatch.setattr(web, "receive_download", lambda *a, **kw: Download())
    record = {"account_id": "same-account", "url": "https://chatgpt.com/c/same", "state": "waiting"}
    web.check_and_refine("same-page", tmp_path, record, request, pending, Event(), lambda _: None, 10)
    assert len(sends) == 1 and sends[0][0] == "same-page"
    assert "SỬA BẢN SAO" in sends[0][1] and "chữ tràn" in sends[0][1]
    assert record["account_id"] == "same-account" and record["quality_followups"] == 1
    assert recorded[0]["quality_stage"] == "preparing"
    assert (tmp_path / "ban-nhap-truoc-sua.pptx").read_bytes() == b"original"
    assert pending.read_bytes() == b"corrected"
    assert (tmp_path / "quality-after.json").exists()
    web.check_and_refine("same-page", tmp_path, record, request, pending, Event(), lambda _: None, 10)
    assert len(sends) == 1


def test_ambiguous_submit_is_never_sent_again_automatically(tmp_path, monkeypatch):
    pending = tmp_path / "result.pptx"
    pending.write_bytes(b"original")
    request = {"config": {"source_file": "source.pptx", "style": "source"}}
    monkeypatch.setattr(web, "inspect_returned_deck", lambda *a: {"slide_quality": quality()})
    monkeypatch.setattr("app.slide_quality.render_quality", lambda p, d, q, *a: q)
    monkeypatch.setattr(web, "write_record", lambda *a: None)
    sends = []

    def ambiguous(*a, **kw):
        sends.append(True)
        raise web.BrowserProblem("submission", "uncertain send")

    monkeypatch.setattr(web, "submit", ambiguous)
    record = {"state": "waiting"}
    with pytest.raises(web.BrowserProblem):
        web.check_and_refine("page", tmp_path, record, request, pending, Event(), lambda _: None, 10)
    web.check_and_refine("page", tmp_path, record, request, pending, Event(), lambda _: None, 10)
    assert sends == [True] and pending.read_bytes() == b"original"


def test_unchanged_correction_stops_without_replacing_best_file(tmp_path, monkeypatch):
    pending = tmp_path / "best.pptx"
    pending.write_bytes(b"best")
    monkeypatch.setattr(web, "inspect_returned_deck", lambda *a: {"slide_quality": quality()})
    monkeypatch.setattr(web, "write_record", lambda *a: None)
    sends = []
    monkeypatch.setattr(web, "submit", lambda *a, **kw: sends.append(True))
    monkeypatch.setattr(web, "wait_result", lambda *a: "link")
    class Download:
        suggested_filename = "fixed.pptx"
        def path(self): return str(pending)
        def save_as(self, path): Path(path).write_bytes(b"not-improved")
    monkeypatch.setattr(web, "receive_download", lambda *a, **kw: Download())
    record = {"state": "waiting"}
    request = {"config": {"source_file": "source.pptx", "style": "source"}}
    web.check_and_refine("same-page", tmp_path, record, request, pending, Event(), lambda _: None, 10)
    assert sends == [True] and pending.read_bytes() == b"best"
    assert record["quality_stop_reason"] == "no_improvement"


def test_correction_repeats_only_while_measured_failures_decrease(tmp_path, monkeypatch):
    pending = tmp_path / "best.pptx"
    pending.write_bytes(b"2")
    def measured(path, *a):
        count = int(Path(path).read_bytes())
        return {"slide_quality": {"slides": [{"slide": 1, "render_image": "", "issues": [
            {"code": "text_overflow", "severity": "FAIL", "shape_id": n} for n in range(count)]}]}}
    monkeypatch.setattr(web, "inspect_returned_deck", measured)
    monkeypatch.setattr(web, "write_record", lambda *a: None)
    sends = []
    monkeypatch.setattr(web, "submit", lambda *a, **kw: sends.append(a[0]))
    monkeypatch.setattr(web, "wait_result", lambda *a: "link")
    class Download:
        suggested_filename = "fixed.pptx"
        def path(self): return str(pending)
        def save_as(self, path): Path(path).write_text(str(2-len(sends)))
    monkeypatch.setattr(web, "receive_download", lambda *a, **kw: Download())
    record = {"state": "waiting", "account_id": "same"}
    web.check_and_refine("same-page", tmp_path, record,
                         {"config": {"source_file": "source.pptx", "style": "source"}},
                         pending, Event(), lambda _: None, 10)
    assert sends == ["same-page", "same-page"] and pending.read_bytes() == b"0"
    assert record["quality_followups"] == 2 and record["quality_stop_reason"] == "complete"
    assert (tmp_path / "ban-nhap-truoc-sua.pptx").read_bytes() == b"2"


@pytest.mark.parametrize("method", ["parallel_columns", "sentence_pairs", "integrated_keywords", "english_only"])
def test_common_prompt_requests_title_exception_real_speech_and_layout_review(method):
    prompt = make_prompt({"title": "Test", "subject": "Vật lý", "education_level": "THPT", "grade": "11",
                          "conversion_format": method, "style": "source", "preset": "standard"}, "source.pptx")
    assert "CHỈ có tiêu đề" in prompt and "Giữ PowerPoint gốc không được thay cả background" in prompt
    assert "Render từng slide" in prompt and "SPEECH:" in prompt and "shape_id" in prompt
    assert "Không cắt bớt lời đọc" in prompt and "Không đọc/ghi vào EN:" in prompt
    payload = next(line.split(":", 1)[1] for line in prompt.splitlines() if line.startswith("SPEECH: {"))
    assert json.loads(payload)["version"] == 1
