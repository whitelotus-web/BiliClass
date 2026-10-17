import json
import wave
import zipfile

import pytest
from pptx import Presentation
from pptx.util import Inches

from app.chatgpt_handoff import external_preview
from app.lesson_narration import audio_status, make_plan
from app.library import Library, RevisionConflict
from app.narration_audio_export import export_audio
from app.readiness import text_readiness
from app.voice_import import import_presentation, prepare_library_lesson, save_script


def source(path, text='', notes=''):
    deck = Presentation()
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    if text:
        slide.shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(2)).text = text
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    deck.slides.add_slide(deck.slide_layouts[6])
    deck.save(path)
    return path


def complete(library, lesson, mode='both'):
    plan, _ = make_plan(lesson, mode, {'voice': 'vieneu:Mai Anh', 'rate': 0}, playback='both_controls' if mode == 'both' else 'separate')
    for keys in plan['keys'].values():
        for key in keys:
            target = library.directory / 'audio' / (key + '.wav')
            target.parent.mkdir(exist_ok=True)
            with wave.open(str(target), 'wb') as writer:
                writer.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                writer.writeframes(b'\1\0' * 100)
    return library.update_narration(lesson['id'], plan)


def test_single_english_notes_are_the_actual_spoken_text_and_blank_slide_is_not_fabricated(tmp_path):
    path = source(tmp_path / 'English.pptx', 'Computer', 'EN: A computer processes information.\nCHECK: Do not read this check.')
    lesson, preview = import_presentation(tmp_path / 'data', path)
    assert lesson['segments'][0]['en'] == 'A computer processes information.'
    assert lesson['segments'][1]['vi'] == lesson['segments'][1]['en'] == ''
    plan, _ = make_plan(lesson, 'en', {'voice': 'vieneu:Mai Anh', 'rate': 0})
    assert plan['total'] == 1 and not plan['skipped']
    library = Library(tmp_path / 'data')
    try:
        lesson = complete(library, lesson, 'en')
        assert audio_status(lesson, library.directory)['ready']
        reviewed = library.review_external_deck(lesson['id'], lesson['revision'])
        assert text_readiness(reviewed, library.directory)['text_ready']
        assert not reviewed['segments'][1]['approved']
        assert external_preview(reviewed, library.directory)['path'] == preview['path']
    finally:
        library.close()


def test_edit_script_preserves_pptx_invalidates_audio_requires_new_review_and_reimports_saved_script(tmp_path):
    path = source(tmp_path / 'Lesson.pptx', 'Máy tính xử lý thông tin.')
    original = path.read_bytes()
    lesson, _ = import_presentation(tmp_path / 'data', path)
    library = Library(tmp_path / 'data')
    try:
        lesson = complete(library, lesson, 'vi')
        lesson = library.review_external_deck(lesson['id'], lesson['revision'])
        changed = save_script(library, lesson['id'], lesson['segments'][0]['id'], lesson['revision'], 'Lời đọc mới.', 'New narration.')
        assert changed['revision'] == lesson['revision'] + 1
        assert not changed['segments'][0]['approved'] and not text_readiness(changed, library.directory)['text_ready']
        assert audio_status(changed, library.directory)['status'] == 'stale'
        assert path.read_bytes() == original
        assert external_preview(changed, library.directory)['revision'] == changed['revision']
        with pytest.raises(RevisionConflict):
            save_script(library, lesson['id'], lesson['segments'][0]['id'], lesson['revision'], 'Old edit.', '')
        again, _ = import_presentation(tmp_path / 'data', path)
        assert again['id'] == changed['id'] and again['segments'][0]['en'] == 'New narration.'
        assert library.get(changed['id'])['narration_variants']
    finally:
        library.close()


def test_blank_presentation_can_receive_script_and_be_prepared_without_design_repair(tmp_path):
    lesson, _ = import_presentation(tmp_path / 'data', source(tmp_path / 'Images.pptx'))
    library = Library(tmp_path / 'data')
    try:
        assert not text_readiness(lesson, library.directory)['text_ready']
        changed = save_script(library, lesson['id'], lesson['segments'][0]['id'], lesson['revision'], 'Xin chào.', '')
        changed['slide_quality'] = {'counts': {'FAIL': 2}}
        library._write(changed)
        reviewed = library.review_external_deck(changed['id'], changed['revision'])
        assert text_readiness(reviewed, library.directory)['text_ready']
        assert reviewed['prepared']['revision'] == reviewed['revision']
        row = library.list_lessons()[0]
        assert row['status'] == 'READY_TO_TEACH' and row['prepared'] and not row['quality_failures']
    finally:
        library.close()


def test_audio_zip_contains_selected_slide_languages_and_matching_audio_without_touching_source(tmp_path):
    path = source(tmp_path / 'Both.pptx', 'Energy', 'VI: Năng lượng được bảo toàn.\nEN: Energy is conserved.')
    before = path.read_bytes()
    lesson, _ = import_presentation(tmp_path / 'data', path)
    library = Library(tmp_path / 'data')
    try:
        lesson = complete(library, lesson)
        target = export_audio(lesson, library.directory, tmp_path / 'Audio.zip')
        with zipfile.ZipFile(target) as archive:
            assert set(archive.namelist()) == {'Slide-001-vi.wav', 'Slide-001-en.wav', 'Slide-001-both.wav', 'loi-doc.txt', 'manifest.json'}
            assert json.loads(archive.read('manifest.json'))['mode'] == 'both'
            assert 'Năng lượng' in archive.read('loi-doc.txt').decode('utf-8')
        assert path.read_bytes() == before
        with pytest.raises(ValueError, match='ngoài thư viện'):
            export_audio(lesson, library.directory, library.directory / 'Bad.zip')
        key = lesson['narration']['keys']['en'][0]
        (library.directory / 'audio' / (key + '.wav')).unlink()
        target.write_bytes(b'existing')
        with pytest.raises(ValueError, match='Tạo đủ'):
            export_audio(lesson, library.directory, target)
        assert target.read_bytes() == b'existing'
    finally:
        library.close()


def test_select_regular_library_lesson_prepares_a_matching_preview(tmp_path, monkeypatch):
    library = Library(tmp_path / 'data')
    lesson = library.create('Bài cũ', 'Tin học', 'THPT', '10', [('Slide 1', 'Máy tính.')])
    lesson = library.edit_segment(lesson['id'], lesson['segments'][0]['id'], 'Máy tính.', 'A computer.')
    library.close()
    monkeypatch.setattr('app.quick_conversion.build_preview', lambda selected, directory, profile: {'lesson_id': selected['id'], 'path': 'prepared.pptx', 'revision': selected['revision']})
    selected, preview = prepare_library_lesson(tmp_path / 'data', lesson['id'])
    assert selected['id'] == preview['lesson_id'] == lesson['id']
    assert preview['revision'] == lesson['revision'] and not selected.get('voice_only')


def test_failed_narration_exposes_cause_and_stops_repeated_failures(tmp_path, monkeypatch):
    from app.narration_preparation import NarrationJob, NarrationPreparation

    job = NarrationJob({'profile': {'units': [{'vi': f'Câu {i}.', 'en': ''} for i in range(20)]}},
                       {'vi': 'vieneu:Mai Anh', 'rate': 0}, tmp_path, None)
    monkeypatch.setattr('app.speech.synthesize_background', lambda *_: (_ for _ in ()).throw(RuntimeError('engine missing')))
    job.run()
    assert job.result['failed'] == 3 and job.result['last_error'] == 'engine missing'
    assert 'engine missing' in NarrationPreparation._completion_message(job.result)
