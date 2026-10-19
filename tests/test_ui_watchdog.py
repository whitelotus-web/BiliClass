import faulthandler
import time
from threading import Event, Thread

from PySide6.QtCore import QCoreApplication

from app.ui_watchdog import UiWatchdog


def until(condition):
    deadline = time.monotonic() + 3
    while not condition():
        assert time.monotonic() < deadline
        time.sleep(.005)


def test_stall_logging_is_safe_during_code_churn_and_never_records_locals(tmp_path, monkeypatch):
    def unsafe(*args, **kwargs):
        raise AssertionError('Native frame walker must never be armed')

    monkeypatch.setattr(faulthandler, 'dump_traceback_later', unsafe)
    app = QCoreApplication.instance() or QCoreApplication([])
    stop = Event()

    def churn():
        while not stop.is_set():
            exec(compile('sum(range(10))', '<temporary-code>', 'exec'), {})

    worker = Thread(target=churn)
    worker.start()
    watcher = UiWatchdog(app, tmp_path, timeout=.05, interval=.01)
    private_lesson_text = 'Private teacher narration must not appear'
    try:
        until(lambda: watcher.path.exists() and '(GUI)' in watcher.path.read_text(encoding='utf-8'))
        first = watcher.path.read_text(encoding='utf-8')
        assert __file__ in first and private_lesson_text not in first
        assert 'line ' in first
        time.sleep(.08)
        assert watcher.path.read_text(encoding='utf-8') == first
        watcher.beat()
        until(lambda: watcher.path.read_text(encoding='utf-8').count('GUI heartbeat delayed:') == 2)
    finally:
        stop.set()
        worker.join(2)
        watcher.stop()
        watcher.thread.join(2)
    assert not watcher.thread.is_alive() and not watcher.timer.isActive()
    before = watcher.path.read_bytes()
    watcher.beat()
    time.sleep(.08)
    assert watcher.path.read_bytes() == before


def test_unwritable_log_cannot_crash_monitor_or_block_shutdown(tmp_path):
    app = QCoreApplication.instance() or QCoreApplication([])
    (tmp_path / 'logs').write_text('A file blocks the log directory')
    watcher = UiWatchdog(app, tmp_path, timeout=.01, interval=.005)
    try:
        time.sleep(.08)
        assert watcher.thread.is_alive()
    finally:
        watcher.stop()
        watcher.thread.join(2)
    assert not watcher.thread.is_alive()
