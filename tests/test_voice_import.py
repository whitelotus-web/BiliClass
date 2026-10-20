import hashlib
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.util import Inches

from app.library import Library
from app.voice_import import import_presentation


def deck(path, text, notes=''):
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    if text:
        slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(2)).text = text
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    presentation.save(path)
    return path


def test_import_keeps_original_bytes_and_language_and_reuses_exact_file(tmp_path):
    source = deck(tmp_path / 'Bài có sẵn.pptx', 'Máy tính giúp xử lý thông tin và lưu trữ dữ liệu.')
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    directory = tmp_path / 'library'
    lesson, preview = import_presentation(directory, source)
    assert lesson['voice_only']
    assert lesson['external_deck']['provider'] == 'voice_import'
    assert lesson['segments'][0]['vi'] and not lesson['segments'][0]['en']
    assert not lesson['segments'][0]['approved']
    assert lesson['source']['sha256'] == before
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert hashlib.sha256(Path(preview['path']).read_bytes()).hexdigest() == before
    again, _ = import_presentation(directory, source)
    assert again['id'] == lesson['id']
    library = Library(directory)
    assert len(library.list_lessons()) == 1
    from app.export_origin import destination

    assert destination(library, again, directory) == (source.parent, source.stem)
    reviewed = library.review_external_deck(lesson['id'], lesson['revision'])
    assert reviewed['segments'][0]['approved']
    from app.readiness import text_readiness

    assert text_readiness(reviewed, directory)['text_ready']
    library.close()


def test_bilingual_notes_available_without_translation(tmp_path):
    source = deck(tmp_path / 'Bilingual.pptx', 'Computer', 'VI: Máy tính xử lý thông tin.\nEN: A computer processes information.')
    lesson, _ = import_presentation(tmp_path / 'library', source)
    assert lesson['segments'][0]['vi'] == 'Máy tính xử lý thông tin.'
    assert lesson['segments'][0]['en'] == 'A computer processes information.'


def test_no_text_can_be_completed_with_explicit_narration_and_wrong_type_rejected(tmp_path):
    source = deck(tmp_path / 'Empty.pptx', '')
    lesson, _ = import_presentation(tmp_path / 'library', source)
    assert not lesson['segments'][0]['vi'] and not lesson['segments'][0]['en']
    assert lesson['voice_only'] and not lesson['segments'][0]['approved']
    wrong = tmp_path / 'image.png'
    wrong.write_bytes(b'not a deck')
    with pytest.raises(ValueError):
        import_presentation(tmp_path / 'library', wrong)
