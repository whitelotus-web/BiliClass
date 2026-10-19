import json
import wave

import pytest

from app import speech, voice_preview


def test_all_bundled_voices_play_without_loading_or_waiting_for_engine(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, '_vieneu_engine', lambda *_: pytest.fail('No engine for preset playback'))
    monkeypatch.setattr(speech, 'synthesis_turn', lambda *_: pytest.fail('Do not queue behind lesson inference'))
    for voice in (*speech.VIENEU_VOICES, *speech.PAIRS):
        for rate in (0, -3, 3):
            result = voice_preview.preview(voice_preview.SAMPLE_TEXT, voice['id'], rate, tmp_path)
            assert speech.valid_audio(result['path'])
            with wave.open(result['path']) as wav:
                assert wav.getframerate() == 48000
            assert voice_preview.preview(voice_preview.SAMPLE_TEXT, voice['id'], rate, tmp_path)['cached']


def test_custom_text_or_incompatible_manifest_uses_real_synthesis(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(speech, 'synthesize', lambda *a: calls.append(a) or {'custom': True})
    voice = speech.VIENEU_VOICES[0]['id']
    assert voice_preview.preview('Câu riêng.', voice, 0, tmp_path) == {'custom': True}
    monkeypatch.setattr(voice_preview, 'SAMPLE_ROOT', tmp_path)
    (tmp_path/'manifest.json').write_text(json.dumps({'engine': 'old', 'text': voice_preview.SAMPLE_TEXT, 'files': {}}))
    assert voice_preview.preview(voice_preview.SAMPLE_TEXT, voice, 0, tmp_path) == {'custom': True}
    assert len(calls) == 2


def test_long_language_samples_and_arbitrary_pair_need_no_model(tmp_path, monkeypatch):
    from app.voice_pairs import compose

    monkeypatch.setattr(speech, 'synthesize', lambda *_: pytest.fail('Bundled long samples must not infer'))
    for voice in speech.VIENEU_VOICES:
        result = voice_preview.preview(voice_preview.VI_SAMPLE_TEXT, voice['id'], 0, tmp_path)
        with wave.open(result['path']) as sample:
            assert 10 < sample.getnframes() / sample.getframerate() < 60
    for voice in speech.ENGLISH_VOICES:
        result = voice_preview.preview(voice_preview.EN_SAMPLE_TEXT, voice, 0, tmp_path)
        assert speech.valid_audio(result['path'])
    voice = compose('vieneu:Mai Anh', 'kokoro-us:am_michael')
    text = voice_preview.VI_SAMPLE_TEXT + '\n' + voice_preview.EN_SAMPLE_TEXT
    for rate in (0, 1):
        result = voice_preview.preview(text, voice, rate, tmp_path)
        assert speech.valid_audio(result['path'])
        assert voice_preview.preview(text, voice, rate, tmp_path)['cached']
