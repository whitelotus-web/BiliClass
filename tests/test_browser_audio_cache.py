from threading import Event

from app.browser_audio import prepare_narration


def test_duplicate_voice_tasks_are_deduplicated_and_existing_wav_reported(monkeypatch, tmp_path):
    calls, messages = [], []

    def synthesize(text, voice, rate, directory):
        calls.append((text, voice, rate))
        return {"cached": True}

    monkeypatch.setattr("app.speech.synthesize", synthesize)
    units = [{"vi": "", "en": "The force acts on the object."} for _ in range(4)]
    result = prepare_narration({"profile": {"units": units}}, {"en": "kokoro:af_heart", "rate": 0},
                               tmp_path, Event(), messages.append)
    assert len(calls) == 1
    assert result["complete"] == result["cached"] == result["total"] == 1
    assert result["duplicates"] == 3 and result["failed"] == 0
