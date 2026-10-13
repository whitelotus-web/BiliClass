import time
import wave
from threading import Event, Thread

from app import speech
from app.narration_preparation import NarrationJob

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
