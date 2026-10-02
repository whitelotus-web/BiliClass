import wave

from app import speech
from app.library import Library
from app.readiness import assess
from app.speech import audio_key, valid_audio


def wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as writer:
        writer.setparams((1, 2, 22050, 0, "NONE", "not compressed"))
        writer.writeframes(b"\x01\x00" * 100)


def test_audio_identity_includes_text_voice_and_rate(tmp_path):
    base = audio_key("Hello", "voice-a", 0)
    assert base != audio_key("Hello!", "voice-a", 0)
    assert base != audio_key("Hello", "voice-b", 0)
    assert base != audio_key("Hello", "voice-a", 1)
    path = tmp_path / "cached.wav"
    assert not valid_audio(path)
    path.write_bytes(b"corrupt")
    assert not valid_audio(path)
    wav(path)
    assert valid_audio(path)


def test_five_kokoro_voices_replace_windows_english_when_model_is_ready(monkeypatch):
    monkeypatch.setattr(speech, "kokoro_ready", lambda: True)
    monkeypatch.setattr(speech, "vieneu_ready", lambda: False)
    monkeypatch.setattr(speech, "_windows_voices", lambda: [
        {"id": "windows-en", "name": "Windows English", "language": "en"},
        {"id": "windows-vi", "name": "Windows Vietnamese", "language": "vi"},
    ])
    voices = speech.list_voices()
    assert [voice["id"] for voice in voices if voice["language"] == "en"] == [
        "kokoro:af_heart", "kokoro:af_bella", "kokoro:am_michael",
        "kokoro:bf_emma", "kokoro:bm_george",
    ]
    assert [voice["id"] for voice in voices if voice["language"] == "vi"] == ["windows-vi"]


def test_vieneu_voices_precede_windows_and_use_offline_synthesizer(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, "kokoro_ready", lambda: False)
    monkeypatch.setattr(speech, "vieneu_ready", lambda: True)
    monkeypatch.setattr(speech, "_windows_voices", lambda: [
        {"id": "windows-vi", "name": "Windows Vietnamese", "language": "vi"}
    ])
    voices = [voice for voice in speech.list_voices() if voice["language"] == "vi"]
    assert [voice["id"] for voice in voices] == [
        "vieneu:Mai Anh", "vieneu:Thùy Dung", "vieneu:Hải Đăng", "vieneu:Thái Sơn", "windows-vi"
    ]
    calls = []

    def render(text, voice, rate, destination):
        calls.append((text, voice, rate))
        wav(destination)

    monkeypatch.setattr(speech, "_synthesize_vieneu", render)
    sample = "Chào các em."
    assert not speech.synthesize(sample, "vieneu:Mai Anh", 0, tmp_path)["cached"]
    assert speech.synthesize(sample, "vieneu:Mai Anh", 0, tmp_path)["cached"]
    assert calls == [(sample, "vieneu:Mai Anh", 0)]
    assert audio_key(sample, "vieneu:Mai Anh", 0) != audio_key(sample, "vieneu:Thùy Dung", 0)


def test_kokoro_audio_is_cached_for_exact_voice_and_speed(tmp_path, monkeypatch):
    calls = []

    def render(text, voice, rate, destination):
        calls.append((text, voice, rate))
        wav(destination)

    monkeypatch.setattr(speech, "_synthesize_kokoro", render)
    first = speech.synthesize("Hello, class.", "kokoro:af_heart", 0, tmp_path)
    second = speech.synthesize("Hello, class.", "kokoro:af_heart", 0, tmp_path)
    third = speech.synthesize("Hello, class.", "kokoro:bf_emma", 0, tmp_path)
    assert first["cached"] is False and second["cached"] is True
    assert third["cached"] is False
    assert len(calls) == 2
    assert audio_key("Hello, class.", "kokoro:af_heart", 0) != audio_key("Hello, class.", "kokoro:af_heart", 1)


def test_readiness_does_not_require_voice_or_quiz_for_text(tmp_path):
    library = Library(tmp_path)
    try:
        lesson = library.create("Bài", "Môn", "THPT", "11", [("Đoạn", "Xin chào.")])
        unreviewed = assess(lesson, tmp_path, [], {"en": "", "vi": ""}, 0)
        assert not unreviewed["text_ready"]
        lesson = library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "Xin chào.", "Hello.", True)
        report = assess(lesson, tmp_path, [], {"en": "", "vi": ""}, 0)
        assert report["text_ready"]
        checks = {c["id"]: c for c in report["checks"]}
        assert not checks["voice_en"]["ok"] and not checks["voice_vi"]["ok"]
        assert "quiz" not in checks and "network" not in checks
    finally:
        library.close()


def test_audio_cache_invalidates_after_content_or_rate_change(tmp_path):
    library = Library(tmp_path)
    try:
        lesson = library.create("Bài", "Môn", "THPT", "11", [("Đoạn", "Xin chào.")])
        lesson = library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "Xin chào.", "Hello.", True)
        voices = [{"id": "v-en"}]
        selections = {"en": "v-en", "vi": ""}
        path = tmp_path / "audio" / (audio_key("Hello.", "v-en", 0) + ".wav")
        wav(path)

        def audio_ready(rate):
            return next(
                c["ok"]
                for c in assess(lesson, tmp_path, voices, selections, rate)["checks"]
                if c["id"] == "audio_en"
            )

        assert audio_ready(0)
        assert not audio_ready(1)
        lesson["segments"][0]["en"] = "Hello there."
        assert not audio_ready(0)
    finally:
        library.close()


def test_readiness_detects_modified_source(tmp_path):
    library = Library(tmp_path / "library")
    try:
        path = tmp_path / "source.txt"
        path.write_text("Source", encoding="utf-8")
        source = library.store_source(path)
        lesson = library.create("Bài", "Môn", "THPT", "11", [("Đoạn", "Gốc")], source)
        lesson = library.edit_segment(lesson["id"], lesson["segments"][0]["id"], "Gốc", "Source", True)
        assert assess(lesson, library.directory, [], {}, 0)["text_ready"]
        (library.directory / "sources" / source["file"]).write_bytes(b"changed")
        report = assess(lesson, library.directory, [], {}, 0)
        assert not report["text_ready"] and not report["checks"][0]["ok"]
    finally:
        library.close()
