import sqlite3
from threading import Event
import zipfile

import pytest

from app.library import Library
from app.library_download import export
from app.library_view import query


def lesson(library, title='Bài thử'):
    value = library.create(title, 'Tin học', 'THPT', '11', [('Slide 1', 'Hệ điều hành quản lý tài nguyên.')])
    return library.edit_segment(value['id'], value['segments'][0]['id'], value['segments'][0]['vi'],
                                'The operating system manages resources.', True)


def test_bulk_trash_validates_every_id_and_keeps_audio_and_restore(tmp_path):
    library = Library(tmp_path)
    one, two = lesson(library), lesson(library)
    wav = library.directory / 'audio' / 'existing.wav'
    wav.parent.mkdir(exist_ok=True); wav.write_bytes(b'keep')
    with pytest.raises(ValueError):
        library.trash_lessons([one['id'], 'missing'])
    assert len(library.list_lessons()) == 2
    assert library.trash_lessons([one['id'], two['id'], one['id']]) == 2
    assert library.list_lessons() == [] and wav.read_bytes() == b'keep'
    assert library.restore_lesson(one['id']) == one
    library.close()


def test_bulk_trash_checks_active_class_before_any_update(tmp_path):
    library = Library(tmp_path)
    one, two = lesson(library), lesson(library)
    import json
    with sqlite3.connect(tmp_path / 'classroom.db') as db:
        db.execute('CREATE TABLE sessions(status TEXT,lesson TEXT)')
        db.execute('INSERT INTO sessions VALUES(?,?)', ('active', json.dumps(two)))
    with pytest.raises(ValueError, match='Kết thúc'):
        library.trash_lessons([one['id'], two['id']])
    assert len(library.list_lessons()) == 2
    library.close()


def test_all_filtered_ids_span_pages_but_exclude_hidden_lessons():
    rows = [{'id': str(i), 'title': str(i), 'subject': 'Toán' if i < 30 else 'Tin học',
             'grade': '11', 'education_level': 'THPT', 'status': 'DRAFT'} for i in range(41)]
    result = query(rows, subject='Toán', page=2)
    assert len(result['rows']) == 10 and result['ids'] == [str(i) for i in range(30)]


def test_bulk_export_duplicate_titles_unique_names_and_no_library_mutation(tmp_path):
    directory = tmp_path / 'library'
    library = Library(directory)
    one, two = lesson(library, '../CON: bài trùng'), lesson(library, '../CON: bài trùng')
    library.close()
    target = tmp_path / 'Bộ bài.zip'
    result = export(directory, [one['id'], two['id']], target)
    assert result['count'] == 2 and result['voiced'] == 0
    with zipfile.ZipFile(target) as archive:
        names = archive.namelist()
        assert len(names) == 3 and len(set(names)) == 3
        assert all('/' not in name and '\\' not in name for name in names)
        assert sum(name.endswith('.pptx') for name in names) == 2
    reopened = Library(directory)
    assert reopened.get(one['id']) == one and reopened.get(two['id']) == two
    reopened.close()


def test_cancel_or_failure_preserves_existing_destination_and_forbids_library(tmp_path):
    directory = tmp_path / 'library'
    library = Library(directory)
    one = lesson(library); library.close()
    target = tmp_path / 'existing.pptx'; target.write_bytes(b'original')
    cancelled = Event(); cancelled.set()
    with pytest.raises(InterruptedError):
        export(directory, [one['id']], target, cancel=cancelled)
    with pytest.raises(ValueError):
        export(directory, [one['id'], 'missing'], target.with_suffix('.zip'))
    with pytest.raises(ValueError, match='ngoài'):
        export(directory, [one['id']], directory / 'bad.pptx')
    assert target.read_bytes() == b'original'


def test_restore_batch_requires_every_entry_still_in_trash(tmp_path):
    library = Library(tmp_path)
    one, two = lesson(library), lesson(library)
    library.trash_lessons([one['id'], two['id']])
    with pytest.raises(ValueError):
        library.restore_lessons([one['id'], 'missing'])
    assert library.list_lessons() == []
    assert library.restore_lessons([one['id'], two['id'], one['id']]) == 2
    assert library.get(one['id']) == one and library.get(two['id']) == two
    library.close()


def test_permanent_delete_rejects_active_or_stale_selection_without_partial_delete(tmp_path):
    library = Library(tmp_path)
    one, active = lesson(library), lesson(library)
    library.trash_lesson(one['id'])
    with pytest.raises(ValueError, match='thùng rác'):
        library.purge_lessons([one['id'], active['id']])
    assert library.get(one['id'], include_trash=True)['deleted_at']
    with pytest.raises(ValueError):
        library.purge_lessons([one['id'], 'missing'])
    library.restore_lesson(one['id'])
    with pytest.raises(ValueError, match='thùng rác'):
        library.purge_lessons([one['id']])
    assert len(library.list_lessons()) == 2
    library.close()


def test_permanent_delete_removes_revisions_but_preserves_shared_files_and_reports(tmp_path):
    import json
    library = Library(tmp_path)
    one, two = lesson(library), lesson(library)
    asset = tmp_path / 'audio' / 'shared.wav'
    asset.parent.mkdir(exist_ok=True); asset.write_bytes(b'shared')
    with sqlite3.connect(tmp_path / 'classroom.db') as db:
        db.execute('CREATE TABLE sessions(status TEXT,lesson TEXT)')
        db.execute('INSERT INTO sessions VALUES(?,?)', ('ended', json.dumps(one)))
    assert library.history(one['id'])
    library.trash_lessons([one['id'], two['id']])
    assert library.purge_lessons([one['id'], two['id'], one['id']]) == 2
    assert library.list_lessons(trash=True) == []
    assert library.db.execute('SELECT COUNT(*) FROM lesson_revisions').fetchone()[0] == 0
    with pytest.raises(ValueError):
        library.restore_lesson(one['id'])
    with sqlite3.connect(tmp_path / 'classroom.db') as db:
        assert db.execute('SELECT COUNT(*) FROM sessions').fetchone()[0] == 1
    assert asset.read_bytes() == b'shared'
    library.close()


def test_permanent_delete_blocks_an_unfinished_class_snapshot(tmp_path):
    import json
    library = Library(tmp_path)
    one = lesson(library)
    library.trash_lesson(one['id'])
    with sqlite3.connect(tmp_path / 'classroom.db') as db:
        db.execute('CREATE TABLE sessions(status TEXT,lesson TEXT)')
        db.execute('INSERT INTO sessions VALUES(?,?)', ('active', json.dumps(one)))
    with pytest.raises(ValueError, match='Kết thúc'):
        library.purge_lessons([one['id']])
    assert len(library.list_lessons(trash=True)) == 1
    library.close()
