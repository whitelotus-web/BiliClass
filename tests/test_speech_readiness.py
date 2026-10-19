import wave

from app import speech
from app.library import Library
from app.readiness import assess
from app.speech import audio_key, valid_audio


def wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as writer:
        writer.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
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


def test_only_multilingual_voices_available_when_model_installed(monkeypatch):
    monkeypatch.setattr(speech, "vieneu_ready", lambda: True)
    monkeypatch.setattr("app.english_speech.ready", lambda: True)
    voices = speech.list_voices()
    assert len(voices) == 9
    assert all(v["provider"] == "local_pair" and v["languages"] == ["vi", "en"] for v in voices)
    assert len({v["id"] for v in voices}) == 9
    monkeypatch.setattr(speech, "vieneu_ready", lambda: False)
    assert speech.list_voices() == []  # Do not pretend a single-language fallback is bilingual.


def test_vieneu_audio_cached_for_exact_voice_text_and_speed(tmp_path, monkeypatch):
    calls = []

    def render(text, voice, rate, destination):
        calls.append((text, voice, rate))
        wav(destination)

    monkeypatch.setattr(speech, "_synthesize_vieneu", render)
    first = speech.synthesize("Hello, class.", "vieneu:Mai Anh", 0, tmp_path)
    second = speech.synthesize("Hello, class.", "vieneu:Mai Anh", 0, tmp_path)
    third = speech.synthesize("Hello, class.", "vieneu:Hải Đăng", 0, tmp_path)
    faster = speech.synthesize("Hello, class.", "vieneu:Mai Anh", 1, tmp_path)
    assert not first["cached"] and second["cached"]
    assert not third["cached"] and not faster["cached"] and len(calls) == 2


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
