import threading
import time
from types import SimpleNamespace

from PySide6.QtCore import QCoreApplication, QObject

from app.system_volume import SystemVolume
from app.teaching_session import TeachingSession


def until(predicate):
    app = QCoreApplication.instance() or QCoreApplication([])
    deadline = time.monotonic() + 3
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    assert predicate()


def test_master_volume_two_way_worker_coalesces_and_ignores_old_events():
    app = QCoreApplication.instance() or QCoreApplication([])
    parent = QObject()
    endpoint, writes, threads = [43, True], [], []
    def backend(target):
        threads.append(threading.get_ident())
        if target is not None:
            writes.append(target)
            endpoint[:] = target, False
        return tuple(endpoint)
    volume = SystemVolume(parent, backend)
    volume.activate(True)
    try:
        until(lambda: volume.available)
        assert volume.value == 43 and volume.muted and not writes, 'Starting must preserve the device state'
        volume.set_value(48)
        until(lambda: volume.value == 48 and not volume.muted)
        until(lambda: endpoint[0] == 48)
        endpoint[:] = 31, True
        until(lambda: volume.value == 31 and volume.muted)
        assert all(identity != threading.get_ident() for identity in threads)
        volume.set_value(110)
        until(lambda: volume.value == 100)
        volume.set_value(-5)
        until(lambda: volume.value == 0)
        generation, worker = volume.generation, volume.worker
        volume.activate(False)
        volume._receive(generation, (0, 90, False, True))
        assert volume.value == 0
        worker.join(1)
        assert not worker.is_alive()
        app.processEvents()
    finally:
        volume.shutdown()


def test_missing_endpoint_recovers_without_writing_windows_volume():
    parent = QObject()
    state = [False]
    def backend(target):
        assert target is None
        if not state[0]:
            raise OSError('No playback device')
        return 62, False
    volume = SystemVolume(parent, backend)
    volume.activate(True)
    try:
        state[0] = True
        until(lambda: volume.available)
        assert volume.value == 62
        state[0] = False
        until(lambda: not volume.available)
        assert volume.value == 62
        state[0] = True
        until(lambda: volume.available)
    finally:
        volume.shutdown()


def test_windows_master_uses_unity_for_native_and_cached_playback(tmp_path):
    from test_teaching_session import FakeBridge

    parent = FakeBridge(tmp_path)
    levels = []
    parent.english_reader.player = SimpleNamespace(set_volume=levels.append)
    session = TeachingSession(parent)
    session.bound = {'lesson': {}}
    session.system_volume.backend = lambda target: (23 if target is None else target, False)
    session._watch_build()
    try:
        until(lambda: session.system_volume.available)
        assert session.volume == 23 and levels[-1] == 100
        assert parent.calls[-1] == ('set_volume', 100)
        session.setVolume(28)
        until(lambda: session.volume == 28)
        assert levels[-1] == 100
        assert parent.calls.count(('set_volume', 100)) == 1, 'Only one attenuation stage'
    finally:
        session.clear()
