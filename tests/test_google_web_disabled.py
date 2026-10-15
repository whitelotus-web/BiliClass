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
    monkeypatch.setattr(slide_repair, 'repair_and_inspect', lambda *args, **kwargs: {'local': True})
    bridge = SimpleNamespace(_busy=False, _lesson={'id': 'lesson', 'revision': 1,
        'external_deck': {'request_id': 'old-job'}}, powerpoint_worker=None,
        library=SimpleNamespace(directory=tmp_path), googleTranslation=True,
        _browser_ai=SimpleNamespace(store=SimpleNamespace(get=forbidden)),
        cancel_event=Event(), inform=lambda *args: None,
        launch=lambda work, complete: queued.append(work))
    ui.Bridge.repairConvertedLesson(bridge)
    assert len(queued) == 1 and queued[0]() == {'local': True}
