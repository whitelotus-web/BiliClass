import json
import wave

import pytest

from app import speech, voice_preview


def test_all_bundled_voices_play_without_loading_or_waiting_for_engine(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, '_vieneu_engine', lambda *_: pytest.fail('No engine for preset playback'))
    monkeypatch.setattr(speech, 'synthesis_turn', lambda *_: pytest.fail('Do not queue behind lesson inference'))
    for voice in speech.VIENEU_VOICES:
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
