import sqlite3
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
