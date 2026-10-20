from types import SimpleNamespace

from PySide6.QtCore import QCoreApplication, QObject

from app.storage_controls import StorageControls


def test_an_unrelated_job_finishing_does_not_mark_a_running_automatic_backup_finished(tmp_path):
    app = QCoreApplication.instance() or QCoreApplication([])
    bridge = QObject()
    bridge.library = SimpleNamespace(directory=tmp_path)
    bridge._automatic_backup = SimpleNamespace(isRunning=lambda: True)
    control = StorageControls(bridge)
    control.begin_backup()
    control.failed()  # Generic job finalization; the independent backup is still running.
    assert control.state['running']
    bridge._automatic_backup.isRunning = lambda: False
    control.finish_backup()
    assert not control.state['running']
    control.deleteLater()
    app.processEvents()
