import time
from threading import Event
from types import SimpleNamespace

from PySide6.QtCore import QCoreApplication, QObject, Signal

from app.classroom_ui import ClassroomBridge
from app.library import Library


class Owner(QObject):
    changed = Signal()
    busy = False


def test_disconnect_waits_for_poll_and_stops_server_without_blocking_gui(tmp_path):
    app = QCoreApplication.instance() or QCoreApplication([])
    owner = Owner()
    owner.library = Library(tmp_path)
    bridge = ClassroomBridge(owner)
    polling, allow_poll, stopping, allow_stop = (Event() for _ in range(4))
    alive = [True]

    def request(_payload):
        polling.set()
        assert allow_poll.wait(5)
        return {'status': 'active', 'session_id': 'fixture'}

    def stop():
        stopping.set()
        assert allow_stop.wait(5)
        alive[0] = False

    bridge.runtime = SimpleNamespace(process=SimpleNamespace(is_alive=lambda: alive[0]),
                                     request=request, stop=stop)
    bridge._url, bridge._qr = 'http://fixture', 'fixture-qr'
    try:
        bridge.poll()
        assert polling.wait(2)
        started = time.monotonic()
        bridge.disconnect()
        assert time.monotonic() - started < .2
        assert bridge.actionBusy and bridge.busy
        bridge.action('end')
        assert bridge._pending is None
        allow_poll.set()
        deadline = time.monotonic() + 5
        while not stopping.is_set():
            app.processEvents()
            assert time.monotonic() < deadline
        assert bridge.busy and bridge.runtime is not None
        allow_stop.set()
        while bridge.busy:
            app.processEvents()
            assert time.monotonic() < deadline
        assert bridge.runtime is None and not bridge.running
        assert not bridge.qrImage and not bridge.joinUrl and not bridge.state
        assert 'Đã tạm đóng' in bridge.message
    finally:
        allow_poll.set()
        allow_stop.set()
        bridge.shutdown()
        app.processEvents()
        owner.library.close()
