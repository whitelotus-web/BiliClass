import sqlite3
from contextlib import closing
from threading import Thread

import pytest

from app.library import Library
from app.library_actions import change


def test_worker_owns_connection_and_preserves_assets_through_trash_restore_purge(tmp_path):
    library = Library(tmp_path)
    one = library.create('Bài thử', 'Toán', 'THPT', '11', [('Tiêu đề', 'Nội dung.')])
    source, audio = tmp_path/'sources'/'shared.pptx', tmp_path/'audio'/'shared.wav'
    source.parent.mkdir(exist_ok=True)
    audio.parent.mkdir(exist_ok=True)
    source.write_bytes(b'original source')
    audio.write_bytes(b'original voice')
    results = []

    def worker():
        for operation in ('trash', 'restore', 'trash', 'purge'):
            results.append(change(tmp_path, operation, [one['id']]))

    task = Thread(target=worker)
    task.start()
    task.join(10)
    assert not task.is_alive() and results == [1, 1, 1, 1]
    assert library.list_lessons() == library.list_lessons(trash=True) == []
    assert source.read_bytes() == b'original source' and audio.read_bytes() == b'original voice'
    library.close()


def test_bulk_trash_locks_before_reading_to_avoid_overwriting_a_concurrent_edit(tmp_path, monkeypatch):
    library = Library(tmp_path)
    one = library.create('Bài thử', 'Toán', 'THPT', '11', [('Tiêu đề', 'Nội dung.')])
    read = library.get

    def read_during_batch(identity):
        value = read(identity)
        with sqlite3.connect(tmp_path/'library.db', timeout=0) as other:
            with pytest.raises(sqlite3.OperationalError, match='locked'):
                other.execute('UPDATE lessons SET title=? WHERE id=?', ('Concurrent edit', identity))
        return value

    monkeypatch.setattr(library, 'get', read_during_batch)
    assert library.trash_lessons([one['id']]) == 1
    assert library.list_lessons(trash=True)[0]['title'] == 'Bài thử'
    library.close()


def test_undo_receipt_restores_only_its_batch_and_preserves_content(tmp_path):
    with closing(Library(tmp_path)) as library:
        lessons = [library.create(f'Bài {n}', 'Toán', 'THPT', '11', [('Slide 1', 'Nội dung.')]) for n in range(3)]
        change(tmp_path, 'trash', [lessons[0]['id']])
        ids = [row['id'] for row in lessons[1:]]
        receipt = change(tmp_path, 'trash', [*ids, ids[0]], with_receipt=True)
        assert set(receipt) == set(ids) and len(set(receipt.values())) == 1
        assert change(tmp_path, 'restore', ids, expected_deleted=receipt) == 2
        assert all(library.get(row['id']) == row for row in lessons[1:])
        assert library.get(lessons[0]['id'], include_trash=True)['deleted_at']


def test_undo_refuses_later_deletion_without_partially_restoring_batch(tmp_path):
    with closing(Library(tmp_path)) as library:
        ids = [library.create(f'Bài {n}', 'Toán', 'THPT', '11', [('Slide 1', 'Nội dung.')])['id'] for n in range(2)]
        receipt = change(tmp_path, 'trash', ids, with_receipt=True)
        library.restore_lesson(ids[0])
        library.trash_lesson(ids[0])
        with pytest.raises(ValueError, match='Lần xóa này đã thay đổi'):
            change(tmp_path, 'restore', ids, expected_deleted=receipt)
        assert len(library.list_lessons(trash=True)) == 2 and not library.list_lessons()


def test_undo_validation_is_locked_and_stale_member_cannot_restore_other_members(tmp_path, monkeypatch):
    with closing(Library(tmp_path)) as library:
        ids = [library.create(f'Bài {n}', 'Toán', 'THPT', '11', [('Slide 1', 'Nội dung.')])['id'] for n in range(2)]
        receipt = library.trash_lessons(ids, with_receipt=True)
        read = library._trash_selection

        def selection_during_restore(selected):
            rows = read(selected)
            with sqlite3.connect(tmp_path/'library.db', timeout=0) as other:
                with pytest.raises(sqlite3.OperationalError, match='locked'):
                    other.execute('DELETE FROM lessons WHERE id=?', (ids[0],))
            return rows

        monkeypatch.setattr(library, '_trash_selection', selection_during_restore)
        assert library.restore_lessons(ids, expected_deleted=receipt) == 2
        library.trash_lessons(ids)
        library.restore_lesson(ids[0])
        with pytest.raises(ValueError, match='thùng rác'):
            library.restore_lessons(ids, expected_deleted=receipt)
        assert library.get(ids[1], include_trash=True)['deleted_at']
