from pathlib import Path

import pytest
from test_teaching_session import prepared_lesson

from app import presentation_audio, teaching_cache
from app.teaching_session import prepare_teaching


def test_reopen_reuses_verified_product_but_each_office_session_owns_its_copy(tmp_path, monkeypatch):
    lesson, preview, directory, source = prepared_lesson(tmp_path)
    original = source.read_bytes()
    calls = []
    embed = presentation_audio.embed_audio
    monkeypatch.setattr(presentation_audio, 'embed_audio', lambda *a, **k: calls.append(1) or embed(*a, **k))
    first = prepare_teaching(lesson, preview, directory)
    second = prepare_teaching(lesson, preview, directory)
    assert calls == [1]
    assert first['owned_path'] != second['owned_path']
    assert first['sha256'] == second['sha256'] and first['media'] == second['media']
    Path(first['owned_path']).unlink()
    assert Path(second['owned_path']).is_file() and source.read_bytes() == original
    # Damaging the derivative cannot silently inject a changed presentation.
    key = teaching_cache.cache_key(lesson, preview['sha256'], directory)
    cache = teaching_cache.load(directory, key)
    cache['path'].write_bytes(b'changed derivative')
    third = prepare_teaching(lesson, preview, directory)
    assert calls == [1, 1] and third['media'] == first['media']
    assert Path(third['owned_path']).is_file()


def test_position_or_audio_change_invalidates_cache_and_missing_voice_never_reuses_it(tmp_path, monkeypatch):
    import os

    lesson, preview, directory, source = prepared_lesson(tmp_path)
    first = prepare_teaching(lesson, preview, directory)
    previous = teaching_cache.cache_key(lesson, preview['sha256'], directory)
    lesson['speaker_position'] = 'top_center'
    assert teaching_cache.cache_key(lesson, preview['sha256'], directory) != previous
    positioned = prepare_teaching(lesson, preview, directory)
    assert positioned['sha256'] != first['sha256']
    before = teaching_cache.cache_key(lesson, preview['sha256'], directory)
    key = next(iter(lesson['narration']['keys']['vi']))
    wav = directory/'audio'/(key+'.wav')
    stamp = wav.stat()
    os.utime(wav, ns=(stamp.st_atime_ns, stamp.st_mtime_ns + 1000000))
    assert teaching_cache.cache_key(lesson, preview['sha256'], directory) != before
    wav.unlink()
    with pytest.raises(ValueError, match='chưa hoàn tất'):
        prepare_teaching(lesson, preview, directory)
    Path(preview['path']).write_bytes(b'changed source')
    with pytest.raises(ValueError, match='thay đổi|không khớp'):
        prepare_teaching(lesson, preview, directory)


def test_current_native_speech_is_reused_without_discarding_saved_script_edits(tmp_path, monkeypatch):
    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    lesson['voice_only'] = False
    monkeypatch.setattr('app.slide_speech.deck_speech', lambda *_: pytest.fail('Current speech must not be re-inspected'))
    prepared = prepare_teaching(lesson, preview, directory)
    assert prepared['speech'] == lesson['slide_speech']


def test_cosmetic_release_keeps_audio_cache_but_format_change_invalidates_it(tmp_path, monkeypatch):
    lesson, preview, directory, _ = prepared_lesson(tmp_path)
    before = teaching_cache.cache_key(lesson, preview['sha256'], directory)
    monkeypatch.setattr('app.__version__', '9.9.9rc999')
    assert teaching_cache.cache_key(lesson, preview['sha256'], directory) == before
    monkeypatch.setattr(teaching_cache, 'FORMAT_VERSION', teaching_cache.FORMAT_VERSION + 1)
    assert teaching_cache.cache_key(lesson, preview['sha256'], directory) != before
