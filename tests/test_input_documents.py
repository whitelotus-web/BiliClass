import threading
import time

from PySide6.QtCore import QCoreApplication

from app.input_documents import InputDocuments


def pump_until(predicate):
    app = QCoreApplication.instance() or QCoreApplication([])
    deadline = time.monotonic() + 5
    while not predicate():
        assert time.monotonic() < deadline
        app.processEvents()
        time.sleep(.002)
    app.processEvents()


def test_slow_file_selection_runs_off_gui_and_only_latest_choice_is_applied(monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    entered, release = threading.Event(), threading.Event()
    calls, results = [], []
    gui_thread = threading.get_ident()

    def validate(urls):
        assert threading.get_ident() != gui_thread
        calls.append(urls)
        if urls == ['first']:
            entered.set()
            assert release.wait(3)
        return {'valid': True, 'name': urls[0]}

    monkeypatch.setattr('app.input_documents.document_selection', validate)
    picker = InputDocuments()
    picker.selected.connect(lambda result, error: results.append((result, error)))
    try:
        started = time.monotonic()
        picker.select(['first'])
        assert time.monotonic() - started < .1 and picker.busy
        pump_until(entered.is_set)
        picker.select(['obsolete'])
        picker.select(['latest'])
        app.processEvents()
        assert not results
        release.set()
        pump_until(lambda: not picker.busy)
        assert calls == [['first'], ['latest']]
        assert results == [({'valid': True, 'name': 'latest'}, '')]
    finally:
        release.set()
        picker.shutdown()


def test_clearing_selection_discards_late_result_and_reports_next_error(monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    entered, release = threading.Event(), threading.Event()
    results = []

    def validate(urls):
        if urls == ['removed']:
            entered.set()
            assert release.wait(3)
            return {'valid': True}
        raise ValueError('Không đọc được tài liệu.')

    monkeypatch.setattr('app.input_documents.document_selection', validate)
    picker = InputDocuments()
    picker.selected.connect(lambda result, error: results.append((result, error)))
    try:
        picker.select(['removed'])
        pump_until(entered.is_set)
        picker.clear()
        assert not picker.busy
        release.set()
        pump_until(lambda: picker.worker is None)
        assert not results
        picker.select(['missing'])
        pump_until(lambda: not picker.busy)
        assert results == [({'valid': False}, 'Không đọc được tài liệu.')]
        app.processEvents()
    finally:
        release.set()
        picker.shutdown()


def test_source_preview_cancels_replaced_file_and_ignores_its_late_image(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from PySide6.QtCore import QObject

    app = QCoreApplication.instance() or QCoreApplication([])
    parent = QObject()
    parent.library = SimpleNamespace(directory=tmp_path)
    entered, cancelled = threading.Event(), threading.Event()
    gui_thread = threading.get_ident()

    def validate(urls):
        return {'valid': True, 'name': urls[0].split('/')[-1], 'url': urls[0]}

    def preview(url, _directory, cancel):
        assert threading.get_ident() != gui_thread
        if url.endswith('first.pptx'):
            entered.set()
            assert cancel.wait(3)
            cancelled.set()
        return {'image': url + '.png', 'total': 2}

    monkeypatch.setattr('app.input_documents.document_selection', validate)
    monkeypatch.setattr('app.input_documents.input_preview', preview)
    picker = InputDocuments(parent)
    try:
        picker.select(['file:///first.pptx'])
        pump_until(entered.is_set)
        assert not picker.busy and picker.preview['busy']
        picker.select(['file:///second.pptx'])
        pump_until(lambda: picker.preview.get('image') == 'file:///second.pptx.png')
        assert cancelled.is_set() and not picker.preview['busy']
        picker.clear()
        app.processEvents()
        assert not picker.preview
    finally:
        picker.shutdown()
