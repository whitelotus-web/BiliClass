from pathlib import Path

import pytest

from app.download_names import presentation_suffix, presentation_title, suggestion


def test_export_names_describe_the_actual_language_and_selected_voice(tmp_path):
    lesson = {'title': 'Bài 1. Hệ điều hành', 'conversion_format': 'parallel_columns'}
    assert suggestion(tmp_path, lesson['title'], presentation_suffix(lesson), 'pptx').name == 'Bài 1. Hệ điều hành (Song ngữ VI-EN).pptx'
    lesson['conversion_format'] = 'english_only'
    assert presentation_suffix(lesson) == 'Tiếng Anh'
    lesson['narration'] = {'mode': 'both', 'voice': 'vieneu:Mai Anh', 'rate': 0}
    assert presentation_suffix(lesson, True) == 'Tiếng Anh - Voice VI-EN'
    lesson['voice_only'] = True
    assert presentation_suffix(lesson) == 'Nguyên bản'


@pytest.mark.parametrize('mode,label', [('vi', 'VI'), ('en', 'EN'), ('both', 'VI-EN')])
def test_bilingual_names_keep_the_original_title_and_actual_voice_languages(tmp_path, mode, label):
    lesson = {'title': 'C3_ÔN TẬP CHƯƠNG 3', 'conversion_format': 'parallel_columns',
              'narration': {'mode': mode, 'voice': 'pair:north-female', 'rate': 0}}
    name = suggestion(tmp_path, presentation_title(lesson), presentation_suffix(lesson, True), 'pptx')
    assert name.name == f'C3_ÔN TẬP CHƯƠNG 3 (Song ngữ VI-EN - Voice {label}).pptx'
    assert 'Voice' not in presentation_suffix(lesson, False)
    name.touch()
    assert suggestion(tmp_path, presentation_title(lesson), presentation_suffix(lesson, True), 'pptx').stem.endswith('(2)')


def test_presentation_title_falls_back_to_the_original_filename():
    assert presentation_title({'source': {'name': 'Ôn tập chương 3.pptx'}}) == 'Ôn tập chương 3'
    assert presentation_title({'title': '  '}) == 'Bài giảng'


def test_library_filename_matches_the_ready_product_instead_of_the_active_incomplete_choice(tmp_path):
    from types import SimpleNamespace

    from PySide6.QtCore import QUrl

    from app.ui import Bridge

    lesson = {'title': 'Bài mẫu', 'conversion_format': 'parallel_columns', 'narration': {'mode': 'none'}}
    bridge = SimpleNamespace(
        downloadsDirectory=QUrl.fromLocalFile(str(tmp_path)).toString(),
        library=SimpleNamespace(get=lambda _: lesson, setting=lambda _key, default: default, directory=tmp_path/'data'),
        _catalog=SimpleNamespace(rows=lambda: [{'id': 'fixture', 'narration': {'variants': [
            {'mode': 'both', 'ready': True}, {'mode': 'en', 'ready': True}, {'mode': 'vi', 'ready': False}]}}]),
    )
    result = Bridge.libraryDownloadSuggestion(bridge, ['fixture'], True)
    assert Path(QUrl(result).toLocalFile()).name == 'Bài mẫu (Song ngữ VI-EN - Voice VI-EN).pptx'
    assert 'Voice' not in Bridge.libraryDownloadSuggestion(bridge, ['fixture'], False)
