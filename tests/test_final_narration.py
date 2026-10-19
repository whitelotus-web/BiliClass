import copy
import zipfile

from test_presentation_audio import fixture

from app.final_narration import available_modes, select_final
from app.lesson_narration import audio_status, variant_id


def test_ready_bilingual_has_all_three_controls_but_unverified_never_hides_creation():
    assert available_modes([{'mode': 'both', 'ready': True, 'playback': 'both_controls'}]) == {
        'vi': True, 'en': True, 'both': True}
    assert available_modes([{'mode': 'en', 'ready': False, 'status': 'checking'}]) == dict.fromkeys(('vi', 'en', 'both'), False)
    assert available_modes([{'mode': 'vi', 'ready': True}]) == {'vi': True, 'en': False, 'both': False}
    assert not available_modes([{'mode': 'both', 'ready': True, 'playback': 'separate'}])['both']


def test_final_download_uses_saved_ready_audio_even_if_active_choice_has_no_voice(tmp_path):
    from app.library_download import export

    library, lesson, source = fixture(tmp_path, 'en')
    lesson['narration'] = {'version': 2, 'mode': 'none'}
    lesson['slide_quality']['counts']['FAIL'] = 0
    library._write(lesson)
    original = source.read_bytes()
    try:
        final = select_final(lesson, library.directory)
        assert audio_status(final, library.directory)['ready'] and final['narration']['mode'] == 'en'
        target = tmp_path/'final.pptx'
        result = export(library.directory, [lesson['id']], target)
        assert result['voiced'] == 1
        with zipfile.ZipFile(target) as archive:
            assert any(name.startswith('ppt/media/') and name.endswith('.wav') for name in archive.namelist())
        assert source.read_bytes() == original and library.get(lesson['id'])['narration']['mode'] == 'none'
        for path in (library.directory/'audio').glob('*.wav'):
            path.unlink()
        target = tmp_path/'without-voice.pptx'
        assert export(library.directory, [lesson['id']], target)['voiced'] == 0
    finally:
        library.close()


def test_final_prefers_complete_bilingual_over_single_language_and_never_uses_stale_audio(tmp_path):
    library, lesson, _ = fixture(tmp_path, 'both')
    try:
        bilingual = copy.deepcopy(lesson['narration'])
        single = {**bilingual, 'mode': 'en', 'keys': {'en': bilingual['keys']['en']}}
        lesson['narration_variants'][variant_id(single)] = single
        lesson['narration'] = single
        assert select_final(lesson, library.directory)['narration']['mode'] == 'both'
        stale = copy.deepcopy(lesson)
        stale['source']['sha256'] = 'f'*64
        assert select_final(stale, library.directory)['narration']['mode'] == 'none'
    finally:
        library.close()
