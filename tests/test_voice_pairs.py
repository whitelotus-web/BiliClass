"""Independent language routes, suggested/custom pairs and legacy-cache safety."""

import copy
import wave
import zipfile
from pathlib import Path

import numpy as np
import pytest
from PySide6.QtCore import QCoreApplication
from test_presentation_audio import fixture
from test_teaching_session import FakeBridge

from app import english_speech, speech
from app.lesson_narration import audio_status, creation_choices, make_plan, variant_id
from app.narration_audio_export import export_audio
from app.presentation_audio import slide_audio
from app.teaching_session import TeachingSession, prepare_teaching
from app.voice_pairs import ALL_PAIRS, PAIRS, compose


def wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as writer:
        writer.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        writer.writeframes(b'\x01\0'*2400)


def test_suggested_pairs_preserve_regional_order_and_include_extra_speakers():
    assert len(PAIRS) == 9 and len({v['id'] for v in PAIRS}) == 9
    assert len(ALL_PAIRS) == 9 * len(speech.ENGLISH_VOICES) and {row['en'] for row in ALL_PAIRS} == set(speech.ENGLISH_VOICES)
    assert [(v['gender'], v['region']) for v in PAIRS[:6]] == [
        (gender, region) for gender in ('Nữ', 'Nam') for region in ('Bắc', 'Trung', 'Nam')]
    assert {(v['region'], v['gender']) for v in PAIRS} == {
        (region, gender) for region in ('Bắc', 'Trung', 'Nam') for gender in ('Nam', 'Nữ')}
    assert {v['vi'] for v in PAIRS} == {v['id'] for v in speech.VIENEU_VOICES}
    for pair in PAIRS[:6]:
        assert pair['en'] == ('kokoro-us:af_heart' if pair['gender'] == 'Nữ' else 'kokoro-us:am_michael')
    assert [(v['vi'], v['en']) for v in PAIRS[6:]] == [
        ('vieneu:Trúc Ly', 'kokoro-us:af_bella'),
        ('vieneu:Đoan Trang', 'kokoro-us:af_heart'),
        ('vieneu:Phạm Tuyên', 'kokoro-us:am_michael')]
    assert len({(v['vi'], v['en']) for v in ALL_PAIRS}) == 9 * len(speech.ENGLISH_VOICES)
    from app.voice_pairs import RECOMMENDED_PAIRS
    assert len(RECOMMENDED_PAIRS) == 9
    assert len({v['en'] for v in RECOMMENDED_PAIRS}) == 8
    assert {v['vi'] for v in RECOMMENDED_PAIRS} == {v['id'] for v in speech.VIENEU_VOICES}


@pytest.mark.parametrize('pair', ALL_PAIRS, ids=lambda row: row['id'])
@pytest.mark.parametrize('mode,languages', [('en', {'en'}), ('vi', {'vi'}), ('both', {'vi', 'en'})])
def test_three_creation_choices_use_correct_speaker_and_only_selected_languages(tmp_path, pair, mode, languages):
    library, lesson, source = fixture(tmp_path)
    try:
        original = source.read_bytes()
        old = copy.deepcopy(lesson['narration'])
        plan, selected = make_plan(lesson, mode, {'voice': pair['id'], 'rate': 0})
        assert plan['playback'] == 'separate' and set(plan['keys']) == languages
        assert {lang for lang in ('vi', 'en') if selected[lang]} == languages
        for lang in languages:
            assert selected[lang] == pair[lang]
            assert set(plan['keys'][lang]).isdisjoint(old['keys'].get(lang, [])) if lang == 'en' else True
            for key in plan['keys'][lang]:
                wav(library.directory/'audio'/(key+'.wav'))
        lesson = library.update_narration(lesson['id'], plan)
        assert audio_status(lesson, library.directory)['ready']
        assert set(slide_audio(lesson, library.directory)[1]) == languages
        choices = creation_choices(lesson, pair['id'], 0)
        assert set(choices) == {'en', 'vi', 'both'}
        assert choices[mode]['id'] == variant_id(plan)
        archive = export_audio(lesson, library.directory, tmp_path/'audio.zip')
        with zipfile.ZipFile(archive) as opened:
            assert {Path(name).stem.rsplit('-', 1)[-1] for name in opened.namelist() if name.endswith('.wav')} == languages
        assert source.read_bytes() == original
        assert audio_status({**lesson, 'narration': old}, library.directory)['ready'], 'Existing multilingual WAVs remain usable'
    finally:
        library.close()


def test_cached_teaching_uses_saved_pair_not_new_global_choice_and_refuses_combined_playback(tmp_path, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    library, lesson, source = fixture(tmp_path)
    try:
        pair = PAIRS[1]
        plan, _ = make_plan(lesson, 'both', {'voice': pair['id'], 'rate': 0})
        for keys in plan['keys'].values():
            for key in keys:
                wav(library.directory/'audio'/(key+'.wav'))
        lesson = library.update_narration(lesson['id'], plan)
        from app.chatgpt_handoff import external_preview

        bridge = FakeBridge(library.directory)
        session = TeachingSession(bridge)
        monkeypatch.setattr(speech, 'synthesize', lambda *a, **k: pytest.fail('Teaching must reuse exact saved audio'))
        session.bind(prepare_teaching(lesson, external_preview(lesson, library.directory), library.directory))
        session.reading_scope = 'visible'
        for language in ('en', 'vi'):
            session.read(language)
            assert session.pending_read[4] == pair[language]
            session.office_event({'event': 'media_stopped', 'token': session.token})
            assert bridge.calls[-1][0][1] == pair[language]
            assert bridge.calls[-1][1] == {'cache_only': True}
        before = list(bridge.calls)
        session.toggleRead('both')
        assert bridge.calls == before and not session.audio['both']
        session.clear()
        app.processEvents()
    finally:
        library.close()


@pytest.mark.parametrize('voice,sid', [('kokoro-us:af_heart', 3), ('kokoro-us:af_bella', 2),
                                    ('kokoro-us:am_michael', 16)])
def test_english_render_keeps_question_and_words_and_outputs_common_pcm_format(tmp_path, monkeypatch, voice, sid):
    from types import SimpleNamespace

    requests = []
    def generate(**request):
        requests.append(request)
        return SimpleNamespace(samples=np.zeros(2400, dtype=np.float32), sample_rate=24000)
    monkeypatch.setattr(english_speech, 'engine', lambda *a: SimpleNamespace(generate=generate))
    path = tmp_path/'new.wav'
    text = 'Do you know? A car is considered a point mass.'
    english_speech.render(text, voice, 0, path)
    assert requests == [{'text': text, 'sid': sid, 'speed': 1.0}]
    with wave.open(str(path)) as reader:
        assert (reader.getnchannels(), reader.getsampwidth(), reader.getframerate(), reader.getnframes()) == (1, 2, 48000, 4800)
    assert speech.audio_key(text, 'kokoro-us:af_heart', 0) != speech.audio_key(text, 'kokoro:af_heart', 0)


def test_missing_english_pack_hides_new_pairs_without_invalidating_saved_voice(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, 'vieneu_ready', lambda: True)
    monkeypatch.setattr(english_speech, 'ready', lambda: False)
    assert not speech.list_voices()
    library, lesson, _ = fixture(tmp_path)
    try:
        assert audio_status(lesson, library.directory)['ready']
    finally:
        library.close()


def test_custom_pair_survives_reopen_and_reuses_each_selected_speakers_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, 'vieneu_ready', lambda: True)
    monkeypatch.setattr('app.english_speech.ready', lambda: True)
    from app.library import Library
    from app.voice_controls import store_preference

    selected = compose('vieneu:Mai Anh', 'kokoro-us:am_michael')
    assert selected and selected not in {row['id'] for row in PAIRS}
    assert compose('vieneu:Mai Anh', 'kokoro-us:af_heart') == 'pair:north-female'
    assert not compose('vieneu:Unknown', 'kokoro-us:am_michael')
    library = Library(tmp_path)
    library.close()
    store_preference(tmp_path, {'voice': selected, 'rate': 1})
    library = Library(tmp_path)
    try:
        saved = speech.voice_settings(library)
        assert (saved['voice'], saved['vi'], saved['en'], saved['rate']) == (
            selected, 'vieneu:Mai Anh', 'kokoro-us:am_michael', 1)
        assert speech.voice_for(selected, 'vi') == speech.voice_for('pair:north-female', 'vi')
        assert speech.voice_for(selected, 'en') == speech.voice_for('pair:north-male', 'en')
    finally:
        library.close()
