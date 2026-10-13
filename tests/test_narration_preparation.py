import time
import wave
from threading import Event, Thread

from app import speech
from app.narration_preparation import NarrationJob, NarrationPreparation

VOICE = "vieneu:Mai Anh"


def write_wave(path):
    with wave.open(str(path), "wb") as writer:
        writer.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        writer.writeframes(b"\x01\x00" * 100)


def test_background_prefetch_cancel_keeps_completed_cache_and_does_not_play(monkeypatch, tmp_path):
    calls = []
    job = NarrationJob({"profile": {"units": [{"vi": "Xin chào.", "en": "Hello."}]}},
                       {"vi": VOICE, "en": VOICE, "rate": 0}, tmp_path, None)

    def synthesize(text, voice, rate, directory, cancel):
        calls.append(text)
        cancel.set()
        return {"cached": True}

    monkeypatch.setattr(speech, "synthesize_background", synthesize)
    monkeypatch.setattr(speech, "play", lambda *_: (_ for _ in ()).throw(AssertionError("Cannot play a draft")))
    job.run()
    assert calls == ["Xin chào."]
    assert job.result["cancelled"] and job.result["complete"] == job.result["cached"] == 1


def test_missing_engine_stops_after_three_failures_not_every_slide(monkeypatch, tmp_path):
    job = NarrationJob({"profile": {"units": [{"vi": f"Câu {i}.", "en": ""} for i in range(50)]}},
                       {"vi": VOICE, "rate": 0}, tmp_path, None)
    monkeypatch.setattr(speech, "synthesize_background", lambda *_: (_ for _ in ()).throw(RuntimeError("engine missing")))
    job.run()
    assert job.result["failed"] == 3 and job.result["total"] == 50
    assert not job.result["cancelled"]


def test_foreground_takes_next_engine_turn_and_same_chunk_is_not_generated_twice(monkeypatch, tmp_path):
    started, release, calls, results, errors = Event(), Event(), [], [], []

    def render(text, voice, rate, path):
        calls.append(text)
        if text == "First background.":
            started.set()
            assert release.wait(5)
        write_wave(path)

    def invoke(function, *args):
        try:
            results.append(function(*args))
        except BaseException as exc:
            errors.append(exc)

    monkeypatch.setattr(speech, "_synthesize_vieneu", render)
    first = Thread(target=invoke, args=(speech.synthesize_background, "First background.", VOICE, 0, tmp_path, Event()))
    foreground = Thread(target=invoke, args=(speech.synthesize, "Shared request.", VOICE, 0, tmp_path))
    background = Thread(target=invoke, args=(speech.synthesize_background, "Shared request.", VOICE, 0, tmp_path, Event()))
    first.start()
    try:
        assert started.wait(5)
        foreground.start()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            with speech._ENGINE_TURN:
                if speech._FOREGROUND_WAITERS == 1:
                    break
            time.sleep(.01)
        assert speech._FOREGROUND_WAITERS == 1
        background.start()
    finally:
        release.set()
        for thread in (first, foreground, background):
            if thread.ident:
                thread.join(5)
    assert not errors and all(not thread.is_alive() for thread in (first, foreground, background))
    assert calls == ["First background.", "Shared request."]
    assert len(results) == 3 and sum(bool(r["cached"]) for r in results) == 1


def test_cancelled_background_waiter_does_not_take_engine_turn(monkeypatch, tmp_path):
    cancel = Event()
    cancel.set()
    monkeypatch.setattr(speech, "_synthesize_vieneu", lambda *_: (_ for _ in ()).throw(AssertionError("Must not infer")))
    import pytest

    with pytest.raises(InterruptedError):
        speech.synthesize_background("Cancelled.", VOICE, 0, tmp_path, cancel)


def test_prefetch_only_synthesizes_missing_or_corrupt_audio_and_keeps_total(monkeypatch, tmp_path):
    texts = ["Đã có.", "Chưa có.", "Cache hỏng."]
    write_wave(tmp_path / (speech.audio_key(texts[0], VOICE, 0) + ".wav"))
    (tmp_path / (speech.audio_key(texts[2], VOICE, 0) + ".wav")).write_bytes(b"broken")
    inspection = {"profile": {"units": [{"vi": text, "en": ""} for text in texts]}}
    job = NarrationJob(inspection, {"vi": VOICE, "rate": 0}, tmp_path, None)
    calls = []
    monkeypatch.setattr(speech, "synthesize_background", lambda text, *args: calls.append(text) or {"cached": False})
    job.run()
    assert calls == texts[1:]
    assert job.result["complete"] == job.result["total"] == 3
    assert job.result["cached"] == 1 and job.result["failed"] == 0
    changed_speed = NarrationJob(inspection, {"vi": VOICE, "rate": 1}, tmp_path, None)
    assert changed_speed.initial_cached == 0 and len(changed_speed.tasks) == 3


def test_reopen_fully_cached_lesson_does_not_start_model_or_reset_progress(monkeypatch, tmp_path):
    text = "Giọng đọc đã sẵn sàng."
    write_wave(tmp_path / (speech.audio_key(text, VOICE, 0) + ".wav"))
    inspection = {"profile": {"units": [{"vi": text, "en": ""}, {"vi": text, "en": ""}]}}
    monkeypatch.setattr(NarrationJob, "start", lambda _: (_ for _ in ()).throw(AssertionError("Must not start a worker")))
    monkeypatch.setattr(speech, "_vieneu_engine", lambda *_: (_ for _ in ()).throw(AssertionError("Must not load model")))
    preparation = NarrationPreparation(tmp_path, None)
    preparation.start("cached-lesson", inspection, {"voice": VOICE, "vi": VOICE, "rate": 0}, tmp_path)
    assert preparation.worker is None and not preparation.state["running"]
    assert preparation.state["complete"] == preparation.state["cached"] == preparation.state["total"] == 1
    assert preparation.state["duplicates"] == 1 and not preparation.state["cancelled"]
    import json

    assert json.loads((tmp_path / "narration-progress.json").read_text(encoding="utf-8"))["complete"] == 1
