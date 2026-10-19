import hashlib
import json
from contextlib import closing

import numpy as np
import pytest

from app import speech
from app.library import Library
from app.voice_speed import time_stretch_audio


def test_legacy_vietnamese_choice_becomes_shared_without_mutating_library(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, "vieneu_ready", lambda: True)
    monkeypatch.setattr("app.english_speech.ready", lambda: True)
    with closing(Library(tmp_path)) as library:
        library.set_setting("voice_vi", "vieneu:Hải Đăng")
        library.set_setting("voice_en", "kokoro:af_bella")
        library.set_setting("voice_rate", -2)
        settings = speech.voice_settings(library)
        assert settings["voice"] == "pair:north-male" and settings["vi"] == "vieneu:Hải Đăng" and settings["en"] == "kokoro-us:am_michael"
        assert settings["rate"] == -2
        assert library.setting("voice_options", None) is None
        assert library.setting("voice_en", "") == "kokoro:af_bella"


def test_atomic_shared_preferences_win_and_survive_reopen(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, "vieneu_ready", lambda: True)
    monkeypatch.setattr("app.english_speech.ready", lambda: True)
    with closing(Library(tmp_path)) as library:
        library.set_setting("voice_vi", "vieneu:Hải Đăng")
        library.set_setting("voice_rate", -3)
        library.set_setting("voice_options", {"voice": "vieneu:Ngọc Trân", "rate": 2})
    with closing(Library(tmp_path)) as library:
        settings = speech.voice_settings(library)
        assert settings["voice"] == "pair:central-female" and settings["vi"] == "vieneu:Ngọc Trân" and settings["en"] == "kokoro-us:af_heart"
        assert settings["rate"] == 2
        assert settings["speed"] == 1.12


def test_missing_model_and_bad_saved_rate_fail_honestly(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, "vieneu_ready", lambda: True)
    monkeypatch.setattr("app.english_speech.ready", lambda: True)
    with closing(Library(tmp_path)) as library:
        library.set_setting("voice_options", {"voice": "removed-speaker", "rate": True})
        settings = speech.voice_settings(library)
        assert settings["voice"] == "pair:north-female" and settings["rate"] == 0
        monkeypatch.setattr(speech, "vieneu_ready", lambda: False)
        settings = speech.voice_settings(library)
        assert settings["en"] == settings["vi"] == "" and settings["index"] == -1


def test_replaced_speed_engine_does_not_reuse_legacy_wav_key():
    old = hashlib.sha256(json.dumps({"text": "Hello", "voice": "vieneu:Mai Anh", "rate": 1,
        "provider": "vieneu-v3-turbo-onnx-fp32-61b85e3-3.8.3"}, sort_keys=True).encode()).hexdigest()
    assert speech.audio_key("Hello", "vieneu:Mai Anh", 1) != old


@pytest.mark.parametrize("rate", [.82, .88, .94, 1., 1.06, 1.12, 1.18])
def test_speed_changes_duration_without_changing_pitch(rate):
    sr = 48000
    time = np.arange(sr * 2, dtype=np.float32) / sr
    tone = (.2 * np.sin(2 * np.pi * 220 * time)).astype(np.float32)
    adjusted = time_stretch_audio(tone, rate, sr)
    assert len(adjusted) == round(len(tone) / rate)
    assert np.isfinite(adjusted).all()
    if rate == 1:
        assert np.array_equal(tone, adjusted)
    middle = adjusted[sr // 4:-sr // 4]
    spectrum = np.abs(np.fft.rfft(middle * np.hanning(len(middle))))
    frequency = np.argmax(spectrum) * sr / len(middle)
    assert abs(frequency - 220) < 2, frequency


@pytest.mark.parametrize("size", [0, 32, 256, 1600])
def test_speed_handles_short_and_silent_audio(size):
    result = time_stretch_audio(np.zeros(size, dtype=np.float32), .82)
    assert np.isfinite(result).all() and not np.any(result)


def test_unsupported_old_voice_is_not_silently_read_with_other_speaker(tmp_path):
    with pytest.raises(ValueError, match="VieNeu"):
        speech.synthesize("Hello", "kokoro:af_heart", 0, tmp_path)


def test_speed_rejects_invalid_input():
    for rate in [0, -1, float("nan"), float("inf")]:
        with pytest.raises(ValueError):
            time_stretch_audio(np.ones(4000, dtype=np.float32), rate)
