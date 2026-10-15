import sqlite3
import threading
import time

from PySide6.QtCore import QCoreApplication, QObject

from app.library import Library
from app.library_catalog import LibraryCatalog


def pump_until(app, condition, timeout=8):
    deadline = time.monotonic() + timeout
    while not condition():
        app.processEvents()
        assert time.monotonic() < deadline, 'Catalog timed out'
        time.sleep(.005)
    app.processEvents()


def test_read_only_catalog_connection_never_writes_or_changes_data_version(tmp_path):
    library = Library(tmp_path)
    library.create('Bài học', 'Toán', 'THCS', '6', [('Một phần tư', 'One quarter')])
    revision = library.db.execute('PRAGMA data_version').fetchone()[0]
    with_read_only = Library.read_only(tmp_path)
    try:
        assert with_read_only.list_lessons(verify_audio=False)[0]['title'] == 'Bài học'
        try:
            with_read_only.set_setting('forbidden', True)
            raise AssertionError('Read-only snapshot accepted a write')
        except sqlite3.OperationalError:
            pass
    finally:
        with_read_only.close()
    assert library.db.execute('PRAGMA data_version').fetchone()[0] == revision
    library.close()


def test_audio_scan_is_background_cached_and_refreshes_latest_edit(tmp_path, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    library = Library(tmp_path)
    lesson = library.create('Bài gốc', 'Toán', 'THCS', '6', [('Một phần tư', 'One quarter')])
    discarded = library.create('Bài trong thùng rác', 'Toán', 'THCS', '6', [('Hai phần tư', 'Two quarters')])
    library.trash_lesson(discarded['id'])
    entered, release = threading.Event(), threading.Event()
    calls = []
    main_thread = threading.get_ident()

    def status(lesson, directory, voices, *, cancel):
        assert threading.get_ident() != main_thread, 'Audio scan ran on GUI thread'
        calls.append(lesson['id'])
        entered.set()
        while not release.wait(.01):
            if cancel.is_set():
                raise InterruptedError()
        return {'status': 'ready', 'mode': 'en', 'ready': True, 'label': 'Có giọng Tiếng Anh'}

    monkeypatch.setattr('app.library_catalog.audio_status', status)
    parent = QObject()
    catalog = LibraryCatalog(library, parent)
    try:
        pump_until(app, lambda: entered.is_set() and bool(catalog.rows()))
        assert catalog.rows()[0]['title'] == 'Bài gốc'
        assert len(catalog.rows(trash=True)) == 1
        for _ in range(100):
            catalog.rows()
            catalog.rows(trash=True)
        assert calls == [lesson['id']], 'Bindings must reuse the published list'
        library.update_metadata(lesson['id'], 'Bài đã sửa', 'Toán', 'THCS', '6')
        catalog.refresh()
        release.set()
        pump_until(app, lambda: catalog.worker is None and catalog.rows()[0]['title'] == 'Bài đã sửa')
        assert catalog.rows()[0]['narration']['ready']
        assert discarded['id'] not in calls, 'Trash must not scan WAVs'
        count = len(calls)
        for _ in range(20):
            app.processEvents()
            catalog.rows()
        assert len(calls) == count, 'Readonly scans must not invalidate their own cache'
        library.restore_lesson(discarded['id'])
        catalog.refresh()
        pump_until(app, lambda: catalog.worker is None and len(catalog.rows()) == 2)
        assert catalog.rows(trash=True) == []
        replacement = Library(tmp_path/'replacement')
        try:
            replacement.create('Thư viện khác', 'Toán', 'THCS', '6', [('Nội dung mới', 'New content')])
            catalog.replace_library(replacement)
            pump_until(app, lambda: catalog.worker is None and len(catalog.rows()) == 1)
            assert catalog.rows()[0]['title'] == 'Thư viện khác'
            assert catalog.rows(trash=True) == []
        finally:
            catalog.shutdown()
            replacement.close()
    finally:
        release.set()
        catalog.shutdown()
        library.close()
