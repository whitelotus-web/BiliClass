import copy
import time
import wave
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.util import Inches
from PySide6.QtCore import QCoreApplication

from app import speech
from app.chatgpt_handoff import inspect_returned_deck
from app.lesson_narration import audio_status, make_plan
from app.library import Library, RevisionConflict
from app.ui import Bridge

VOICE = "vieneu:Mai Anh"
VOICES = {"voice": VOICE, "vi": VOICE, "en": VOICE, "rate": 0}


def wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as writer:
        writer.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
        writer.writeframes(b"\x01\x00" * 100)


@pytest.fixture
def saved(tmp_path):
    path = tmp_path / "lesson.pptx"
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    slide.shapes.add_textbox(Inches(1), Inches(1), Inches(7), Inches(2)).text = "Năng lượng được bảo toàn.\nEnergy is conserved."
    slide.notes_slide.notes_text_frame.text = "VI: Năng lượng được bảo toàn.\nEN: Energy is conserved."
    deck.save(path)
    library = Library(tmp_path / "library")
    config = {"title": "Test", "subject": "Vật lý", "education_level": "THPT", "grade": "10",
              "conversion_format": "parallel_columns", "style": "source", "preset": "standard"}
    lesson = library.create_external_lesson(config, library.store_source(path), inspect_returned_deck(path))
    yield library, lesson, path
    library.close()


@pytest.mark.parametrize("mode,languages", [("en", {"en"}), ("vi", {"vi"}), ("both", {"vi", "en"})])
def test_selected_languages_only_and_metadata_does_not_approve_or_change_pptx(saved, mode, languages):
    library, lesson, path = saved
    original = path.read_bytes()
    plan, selected = make_plan(lesson, mode, VOICES)
    assert set(plan["keys"]) == languages
    assert {lang for lang in ("vi", "en") if selected[lang]} == languages
    for keys in plan["keys"].values():
        for key in keys:
            wav(library.directory / "audio" / (key + ".wav"))
    changed = library.update_narration(lesson["id"], plan)
    assert changed["revision"] == lesson["revision"] and changed["created_at"] == lesson["created_at"]
    assert not any(s["approved"] for s in changed["segments"])
    status = audio_status(changed, library.directory, VOICES)
    assert status["ready"] and set(status["languages"]) == languages
    assert library.list_lessons()[0]["narration"]["mode"] == mode
    assert path.read_bytes() == original


def test_new_conversion_has_no_voice_even_if_other_lessons_cached_identical_text(saved):
    library, lesson, _ = saved
    plan, _ = make_plan(lesson, "both", VOICES)
    for keys in plan["keys"].values():
        for key in keys:
            wav(library.directory / "audio" / (key + ".wav"))
    assert audio_status(lesson, library.directory, VOICES)["status"] == "none"
    assert library.list_lessons()[0]["narration"]["status"] == "none"


def test_legacy_cached_voice_is_recognized_without_loading_or_starting_model(saved, monkeypatch):
    library, lesson, _ = saved
    lesson.pop("narration")
    plan, _ = make_plan(lesson, "en", VOICES)
    for key in plan["keys"]["en"]:
        wav(library.directory / "audio" / (key + ".wav"))
    monkeypatch.setattr(speech, "_vieneu_engine", lambda *_: (_ for _ in ()).throw(AssertionError("No model")))
    status = audio_status(lesson, library.directory, VOICES)
    assert status["ready"] and status["mode"] == "en" and status["complete"] == status["total"]


def test_missing_or_corrupt_wavs_and_unrelated_keys_cannot_claim_ready(saved):
    library, lesson, _ = saved
    plan, _ = make_plan(lesson, "en", VOICES)
    lesson["narration"] = plan
    path = library.directory / "audio" / (plan["keys"]["en"][0] + ".wav")
    wav(path)
    assert audio_status(lesson, library.directory)["ready"]
    path.write_bytes(b"broken")
    assert not audio_status(lesson, library.directory)["ready"]
    forged = "f" * 64
    wav(path.parent / (forged + ".wav"))
    lesson["narration"]["keys"]["en"] = [forged]
    assert audio_status(lesson, library.directory)["status"] == "stale"


def test_late_audio_metadata_cannot_overwrite_edited_lesson(saved):
    library, lesson, _ = saved
    plan, _ = make_plan(lesson, "en", VOICES)
    changed = copy.deepcopy(lesson)
    changed["segments"][0]["en"] = "Changed content."
    library._write(changed)
    with pytest.raises(RevisionConflict):
        library.update_narration(lesson["id"], plan)
    assert library.get(lesson["id"])["narration"]["mode"] == "none"


def test_explicit_local_generation_cache_reuse_and_reopen_do_not_send_web_request(saved, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    library, lesson, path = saved
    calls = []
    monkeypatch.setattr(speech, "list_voices", lambda: [{"id": VOICE, "provider": "vieneu", "languages": ["vi", "en"]}])
    monkeypatch.setattr("app.browser_automation.convert", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("No web request")))
    def render(text, voice, rate, directory, cancel):
        calls.append(text)
        target = Path(directory) / (speech.audio_key(text, voice, rate) + ".wav")
        wav(target)
        return {"path": str(target), "cached": False}
    monkeypatch.setattr(speech, "synthesize_background", render)
    bridge = Bridge(library)
    try:
        bridge._lesson = lesson
        assert bridge.lessonNarration["status"] == "none" and not calls
        bridge.createLessonNarration("en")
        deadline = time.monotonic() + 5
        while bridge.narrationBusy and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        assert not bridge.narrationBusy and bridge.lessonNarration["ready"]
        assert calls == ["Energy is conserved."]
        assert bridge._lesson_voice_settings()["vi"] == ""
        bridge.createLessonNarration("en")
        assert not bridge.narrationBusy and len(calls) == 1
        assert library.get(lesson["id"])["revision"] == lesson["revision"]
        assert path.read_bytes() == (library.directory / "sources" / lesson["source"]["file"]).read_bytes()
        bridge.speakSegment("vi")
        assert len(calls) == 1 and "chưa chọn giọng" in bridge.message
    finally:
        bridge.narration_preparation.shutdown()
        bridge.english_reader.shutdown()
        bridge.browserAI.shutdown()
