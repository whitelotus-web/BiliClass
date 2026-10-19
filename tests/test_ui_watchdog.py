from PySide6.QtCore import QCoreApplication

from app.ui_watchdog import UiWatchdog


def test_ui_watchdog_resets_deadline_and_closes_before_shutdown(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr('app.ui_watchdog.faulthandler.dump_traceback_later',
                        lambda delay, **kwargs: calls.append((delay, kwargs['file'])))
    monkeypatch.setattr('app.ui_watchdog.faulthandler.cancel_dump_traceback_later', lambda: calls.append('cancel'))
    app = QCoreApplication.instance() or QCoreApplication([])
    watcher = UiWatchdog(app, tmp_path)
    assert watcher.timer.isActive() and calls[0][0] == 5
    watcher.beat()
    assert len(calls) == 2 and calls[0][1] is calls[1][1]
    watcher.stop()
    assert watcher.output.closed and not watcher.timer.isActive() and calls[-1] == 'cancel'
    before = len(calls)
    watcher.beat()
    assert len(calls) == before
