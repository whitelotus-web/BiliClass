import threading
import time

from PySide6.QtCore import QCoreApplication, QObject

from app.narration_status import NarrationStatus


def until(app, condition):
    deadline = time.monotonic() + 4
    while not condition():
        app.processEvents()
        assert time.monotonic() < deadline
        time.sleep(.005)
    app.processEvents()


def test_slow_wav_checks_do_not_block_gui_and_discard_old_selection(tmp_path, monkeypatch):
    app = QCoreApplication.instance() or QCoreApplication([])
    owner = QObject()
    state = NarrationStatus(owner)
    entered, release = threading.Event(), threading.Event()
    calls = []
    main_thread = threading.get_ident()

    def check(lesson, directory, voices, *, cancel):
        assert threading.get_ident() != main_thread
        calls.append(lesson['id'])
        entered.set()
        assert release.wait(3)
        return {'ready': True, 'mode': 'en', 'voice': lesson['id']}

    monkeypatch.setattr('app.narration_status.audio_status', check)
    try:
        state.refresh(tmp_path, {'id': 'first'}, {})
        until(app, entered.is_set)
        for _ in range(100):
            assert not state.state['ready']
            state.refresh(tmp_path, {'id': 'first'}, {})
            app.processEvents()
        assert calls == ['first']
        state.refresh(tmp_path, {'id': 'second'}, {})
        release.set()
        until(app, lambda: state.worker is None)
        assert calls == ['first', 'second'] and state.state['voice'] == 'second'
        state.refresh(tmp_path, {'id': 'second'}, {}, force=True)
        until(app, lambda: state.worker is None)
        assert calls == ['first', 'second', 'second']
        state.refresh(tmp_path, {}, {})
        assert state.state == {} and state.worker is None
    finally:
        release.set()
        state.shutdown()
