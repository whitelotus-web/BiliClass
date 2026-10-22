import json
from unittest.mock import Mock

import pytest

from app.lesson_location import presentation_location, select_in_explorer
from app.lesson_narration import variant_id
from app.library import Library


@pytest.fixture
def saved(tmp_path):
    library = Library(tmp_path / 'data')
    lesson = library.create('Bài Toán', 'Toán', 'THPT', '11', [('Một', 'One')])
    source = library.directory / 'sources' / 'managed.pptx'
    source.parent.mkdir(exist_ok=True)
    source.write_bytes(b'local presentation')
    lesson['source'] = {'file': source.name}
    library.db.execute('UPDATE lessons SET content=? WHERE id=?', (json.dumps(lesson), lesson['id']))
    library.db.commit()
    yield library, lesson, source
    library.close()


def remember(library, lesson, path, record='no_voice', **extra):
    value = dict(lesson_id=lesson['id'], record_id=record, revision=lesson['revision'], path=str(path), **extra)
    library.set_setting('completed_export:' + lesson['id'] + ':' + record + ':' + path.stem, value)


def test_existing_export_including_teacher_edits_is_found_read_only(saved, tmp_path):
    library, lesson, source = saved
    output = tmp_path / 'Bài mới, #1 (Song ngữ).pptx'
    output.write_bytes(b'teacher manually edited this file')
    remember(library, lesson, output, sha256='old hash')
    before = library.get(lesson['id'])
    assert presentation_location(library.directory, lesson['id']) == output
    assert library.get(lesson['id']) == before
    assert source.read_bytes() == b'local presentation'
    assert output.read_bytes() == b'teacher manually edited this file'


def test_missing_export_falls_back_to_managed_file(saved, tmp_path):
    library, lesson, source = saved
    remember(library, lesson, tmp_path / 'missing.pptx')
    assert presentation_location(library.directory, lesson['id']) == source
    source.unlink()
    with pytest.raises(ValueError, match='Không tìm thấy file'):
        presentation_location(library.directory, lesson['id'])


def test_selected_voice_export_precedes_unvoiced_file(saved, tmp_path):
    library, lesson, _ = saved
    record = dict(mode='en', signature='fixture', voice='voice', rate=0)
    lesson['narration'] = record
    library.db.execute('UPDATE lessons SET content=? WHERE id=?', (json.dumps(lesson), lesson['id']))
    library.db.commit()
    plain, voice = tmp_path / 'plain.pptx', tmp_path / 'voice.pptx'
    plain.write_bytes(b'no voice')
    voice.write_bytes(b'with voice')
    remember(library, lesson, plain)
    remember(library, lesson, voice, variant_id(record))
    assert presentation_location(library.directory, lesson['id']) == voice


def test_invalid_or_foreign_shortcut_is_not_used(saved, tmp_path):
    library, lesson, source = saved
    file = tmp_path / 'foreign.pptx'
    file.write_bytes(b'foreign')
    library.set_setting('completed_export:' + lesson['id'] + ':no_voice:foreign',
                        dict(lesson_id='someone-else', record_id='no_voice', path=str(file)))
    library.set_setting('completed_export:' + lesson['id'] + ':no_voice:broken', ['invalid'])
    assert presentation_location(library.directory, lesson['id']) == source


def test_shell_receives_exact_unicode_path_without_command_parsing(tmp_path, monkeypatch):
    import os
    if os.name != 'nt':
        pytest.skip('Windows shell adapter')
    from win32com.shell import shell
    path = tmp_path / 'Bài mới, #1.pptx'
    parse, reveal = Mock(return_value=('pidl', 0)), Mock()
    monkeypatch.setattr(shell, 'SHParseDisplayName', parse)
    monkeypatch.setattr(shell, 'SHOpenFolderAndSelectItems', reveal)
    assert select_in_explorer(path)
    parse.assert_called_once_with(str(path), 0)
    reveal.assert_called_once_with('pidl', [], 0)
