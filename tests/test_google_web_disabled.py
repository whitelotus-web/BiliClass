"""Old saved lessons must not reactivate the browser through the repair button."""
from threading import Event
from types import SimpleNamespace


def test_repair_of_old_web_lesson_uses_only_local_repair_in_google_mode(tmp_path, monkeypatch):
    from app import slide_refinement, slide_repair, ui

    def forbidden(*args, **kwargs):
        raise AssertionError('Browser account/repair was used in Google mode')

    queued = []
    folder = tmp_path / 'chatgpt' / 'old-job'
    folder.mkdir(parents=True)
    (folder / 'browser-job.json').write_text('{"account_id":"old-account"}')
    monkeypatch.setattr(ui, 'verified_presentation', lambda *args: tmp_path / 'saved.pptx')
    monkeypatch.setattr(slide_refinement, 'repair_existing', forbidden)
    repaired = {'local': True, 'path': str(tmp_path / 'sources' / 'saved.pptx')}
    calls = []
    def local_repair(path, directory, **options):
        calls.append((path, directory, options))
        return repaired
    monkeypatch.setattr(slide_repair, 'repair_and_inspect', local_repair)
    bridge = SimpleNamespace(_busy=False, _lesson={'id': 'lesson', 'revision': 1,
        'source': {'file': 'saved.pptx'}, 'external_deck': {'request_id': 'old-job'}}, powerpoint_worker=None,
        library=SimpleNamespace(directory=tmp_path), googleTranslation=True,
        _browser_ai=SimpleNamespace(store=SimpleNamespace(get=forbidden)),
        cancel_event=Event(), inform=lambda *args: None,
        launch=lambda work, complete: queued.append(work))
    ui.Bridge.repairConvertedLesson(bridge)
    assert len(queued) == 1 and queued[0]() == repaired
    assert calls[0][0] == tmp_path / 'sources' / 'saved.pptx'
    assert calls[0][1] == tmp_path and calls[0][2]['source'] is None


def test_key_save_readback_failure_preserves_the_input(monkeypatch):
    from PySide6.QtCore import QCoreApplication, QObject

    from app.google_settings import GoogleSettings

    app = QCoreApplication.instance() or QCoreApplication([])
    class FakeBridge(QObject):
        def __init__(self):
            super().__init__()
            self._busy = False
            self.library = SimpleNamespace(setting=lambda *args: 500000, set_setting=lambda *args: None)
            self.messages = []
        def inform(self, message, error=False):
            self.messages.append((message, error))
    class Store:
        def public(self):
            raise ValueError('Không đọc lại được key đã mã hóa.')
        def add(self, text):
            pass
    monkeypatch.setattr(GoogleSettings, 'store', lambda self: Store())
    bridge = FakeBridge()
    settings = GoogleSettings(bridge)
    assert settings.save('AIza' + 'a' * 35, 500000) is False
    assert settings.state['configured'] is False
    assert bridge.messages[-1][1] is True
    app.processEvents()
