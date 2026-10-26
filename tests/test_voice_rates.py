import hashlib
import json
import wave
from contextlib import closing

import numpy as np
import pytest

from app import speech, voice_preview
from app.browser_audio import narration_tasks
from app.lesson_narration import audio_status, make_plan, variant_id, variant_title
from app.library import Library
from app.narration_preparation import NarrationJob
from app.voice_rates import rate_choices, rate_for, speed_for, valid_rate
from app.voice_speed import time_stretch_audio


def test_saved_rates_keep_old_meanings_and_add_three_slower_options():
    assert [row['percent'] for row in rate_choices()] == [60, 70, 75, 82, 88, 94, 100, 106, 112, 118]
    assert all(speed_for(rate) == speech._SPEEDS[rate + 3] for rate in range(-3, 4))
    assert not any(valid_rate(rate) for rate in (True, 0., None, -7, 4))


@pytest.mark.parametrize('speed', [.6, .7, .75])
def test_new_slow_rates_lengthen_audio_without_lowering_test_tone_pitch(speed):
    sr = 48000
    source = (.2 * np.sin(2 * np.pi * 220 * np.arange(sr * 2) / sr)).astype(np.float32)
    output = time_stretch_audio(source, speed, sr)
    assert len(output) == round(len(source) / speed) and np.isfinite(output).all()
    middle = output[sr // 4:-sr // 4]
    frequency = np.argmax(abs(np.fft.rfft(middle * np.hanning(len(middle))))) * sr / len(middle)
    assert abs(frequency - 220) < 2


def test_first_use_and_separate_preferences_survive_restart_without_changing_legacy(tmp_path):
    with closing(Library(tmp_path)) as library:
        assert speech.voice_settings(library, speech.PAIRS)['rate'] == 0
        assert speech.voice_settings(library, speech.PAIRS)['en_rate'] == 0
        library.set_setting('voice_options', dict(voice='pair:north-female', rate=-4, vi_rate=-4, en_rate=0))
    with closing(Library(tmp_path)) as library:
        settings = speech.voice_settings(library, speech.PAIRS)
        assert rate_for(settings, 'vi') == -4 and rate_for(settings, 'en') == 0
        library.set_setting('voice_options', dict(voice='pair:north-female', rate=-2))
        settings = speech.voice_settings(library, speech.PAIRS)
        assert settings['vi_rate'] == settings['en_rate'] == -2


def test_language_speeds_drive_audio_keys_worker_and_saved_variant_independently(tmp_path, monkeypatch):
    with closing(Library(tmp_path)) as library:
        lesson = library.create('Bài thử', 'Toán', 'THPT', '11', [('Slide 1', 'Xin chào các em.')])
        segment = lesson['segments'][0]
        lesson = library.edit_segment(lesson['id'], segment['id'], 'Xin chào các em.', 'Hello everyone.', True)
        options = dict(voice='pair:north-female', rate=-4, en_rate=0)
        plan, selected = make_plan(lesson, 'both', options)
        inspection = {'profile': {'units': [dict(vi='Xin chào các em.', en='Hello everyone.')]}}
        tasks, _, _ = narration_tasks(inspection, selected, include_rates=True)
        assert {voice: rate for _, voice, rate in tasks} == {selected['vi']: -4, selected['en']: 0}
        calls = []

        def synthesize(text, voice, rate, directory, *_):
            calls.append((voice, rate))
            directory.mkdir(exist_ok=True)
            with wave.open(str(directory / (speech.audio_key(text, voice, rate) + '.wav')), 'wb') as writer:
                writer.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
                writer.writeframes(b'\1\0' * 480)
            return dict(cached=False)

        monkeypatch.setattr(speech, 'synthesize_background', synthesize)
        job = NarrationJob(inspection, selected, tmp_path / 'audio', None)
        job.run()
        assert job.result['failed'] == 0 and len(calls) == 2
        assert audio_status({**lesson, 'narration': plan}, tmp_path)['ready']
        assert 'Việt 75% · Anh 100%' in variant_title(plan)
        changed, _ = make_plan(lesson, 'both', {**options, 'en_rate': -6})
        assert changed['keys']['vi'] == plan['keys']['vi'] and changed['keys']['en'] != plan['keys']['en']
        assert variant_id(plan) != variant_id(changed)
        old, _ = make_plan(lesson, 'both', dict(voice=options['voice'], rate=0))
        same, _ = make_plan(lesson, 'both', dict(voice=options['voice'], rate=0, en_rate=0))
        assert old == same and variant_id(old) == variant_id(same)
        library.update_narration(lesson['id'], plan)
        library.update_narration(lesson['id'], changed)
        stored = library.get(lesson['id'])
        assert stored['narration']['en_rate'] == -6
        assert variant_id(plan) in stored['narration_variants']


def test_pair_preview_keeps_legacy_cache_and_uses_separate_language_rates(tmp_path, monkeypatch):
    text, voice = voice_preview.VI_SAMPLE_TEXT + '\n' + voice_preview.EN_SAMPLE_TEXT, 'pair:north-female'
    legacy = hashlib.sha256(json.dumps([text, voice, 0, speech.VIENEU_VERSION, speech.ENGLISH_VERSION]).encode()).hexdigest()
    assert voice_preview.pair_preview_key(text, voice, 0, 0) == legacy
    calls = []
    real_preview = voice_preview.preview

    def preview(sentence, identity, rate, directory, **_):
        calls.append((identity, rate))
        destination = tmp_path / f'{len(calls)}.wav'
        with wave.open(str(destination), 'wb') as writer:
            writer.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
            writer.writeframes(b'\1\0' * 480)
        return dict(path=str(destination), cached=False)

    monkeypatch.setattr(voice_preview, 'preview', preview)
    result = real_preview(text, voice, -4, tmp_path, en_rate=0)
    assert speech.valid_audio(result['path'])
    assert calls == [(speech.voice_for(voice, 'vi'), -4), (speech.voice_for(voice, 'en'), 0)]


@pytest.mark.parametrize('mode,rate', [('en', 0), ('vi', -4)])
def test_single_language_narration_keeps_its_own_speed(tmp_path, mode, rate):
    with closing(Library(tmp_path)) as library:
        lesson = library.create('Bài thử', 'Toán', 'THPT', '11', [('Slide 1', 'Xin chào.')])
        part = lesson['segments'][0]
        lesson = library.edit_segment(lesson['id'], part['id'], 'Xin chào.', 'Hello.', True)
        plan, _ = make_plan(lesson, mode, dict(voice='pair:north-female', rate=-4, en_rate=0))
        same, _ = make_plan(lesson, mode, dict(voice='pair:north-female', rate=rate))
        assert plan['rate'] == rate and plan == same
