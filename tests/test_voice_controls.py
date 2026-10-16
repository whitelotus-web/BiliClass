import socket
import sqlite3
import time
from threading import Event
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QThread, Signal

from app.classroom_ui import ClassroomBridge
from app.library import Library
from app.voice_controls import VoiceControls


@pytest.fixture(scope='session')
def qt():
    return QCoreApplication.instance() or QCoreApplication([])


def wait(qt, condition, timeout=4):
    deadline = time.perf_counter() + timeout
    beats = 0
    while not condition() and time.perf_counter() < deadline:
        qt.processEvents()
        time.sleep(.005)
        beats += 1
    assert condition()
    return beats


def test_preferences_save_during_slow_preview_and_ignore_cancelled_audio(qt, tmp_path, monkeypatch):
    library = Library(tmp_path)
    control = VoiceControls(tmp_path, qt)
    started, release = Event(), Event()
    def preview(text, *_, cancel):
        if text == 'slow':
            started.set()
            release.wait(2)
        return {'path': text, 'cached': True}
    monkeypatch.setattr('app.voice_preview.preview', preview)
    played = []
    control.ready.connect(played.append)
    control.preview('slow', 'vieneu:Mai Anh', 0)
    wait(qt, started.is_set)
    control.save('vieneu:Hải Đăng', 2)
    wait(qt, lambda: control.save_worker is None)
    assert library.setting('voice_options', {}) == {'voice':'vieneu:Hải Đăng', 'rate':2}
    assert control.phase == 'preparing' and not control.save_error
    control.preview('latest', 'vieneu:Hải Đăng', 2)
    wait(qt, lambda: len(played) == 1)
    release.set()
    wait(qt, lambda: not control.preview_workers)
    assert [row['path'] for row in played] == ['latest']
    control.shutdown()
    control.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    library.close()


def test_locked_database_does_not_block_qt_or_report_false_success(qt, tmp_path):
    library = Library(tmp_path)
    library.set_setting('voice_options', {'voice':'vieneu:Mai Anh', 'rate':0})
    locker = sqlite3.connect(tmp_path/'library.db')
    locker.execute('BEGIN EXCLUSIVE')
    control = VoiceControls(tmp_path, qt)
    mark = time.perf_counter()
    control.save('vieneu:Hải Đăng', 2)
    assert time.perf_counter() - mark < .2
    beats = wait(qt, lambda: control.save_worker is None)
    assert control.save_error and 'Chưa lưu' in control.save_message
    assert beats > 30
    locker.rollback()
    locker.close()
    assert library.setting('voice_options', {}) == {'voice':'vieneu:Mai Anh','rate':0}
    control.save('vieneu:Hải Đăng', 2)
    wait(qt, lambda: control.save_worker is None)
    assert not control.save_error
    assert library.setting('voice_options', {}) == {'voice':'vieneu:Hải Đăng','rate':2}
    control.shutdown()
    control.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    library.close()


def test_network_interfaces_are_a_snapshot_and_scan_once_off_gui(qt, tmp_path, monkeypatch):
    class Bridge(QObject):
        changed = Signal()
        def __init__(self):
            super().__init__()
            self.library = Library(tmp_path)
    calls = []
    def stats():
        assert QThread.currentThread() != qt.thread()
        calls.append('scan')
        time.sleep(.1)
        return {'Wi-Fi': SimpleNamespace(isup=True)}
    monkeypatch.setattr('app.classroom_ui.psutil.net_if_stats', stats)
    monkeypatch.setattr('app.classroom_ui.psutil.net_if_addrs', lambda: {
        'Wi-Fi':[SimpleNamespace(family=socket.AF_INET,address='192.168.0.3')]})
    bridge = Bridge()
    classroom = ClassroomBridge(bridge)
    for _ in range(5):
        assert classroom.interfaces
        bridge.changed.emit()
    assert not calls
    classroom.refreshInterfaces()
    classroom.refreshInterfaces()
    wait(qt, lambda: not classroom.scanningInterfaces)
    for _ in range(10):
        assert classroom.interfaces[0]['host'] == '192.168.0.3'
    assert calls == ['scan']
    classroom.shutdown()
    bridge.library.close()


def test_subject_theme_covers_all_catalogue_subjects_and_spelling_variants(qt):
    from PySide6.QtQml import QJSEngine

    from app.paths import RESOURCE_ROOT
    from app.school_subjects import CURRICULUM_SUBJECTS

    engine = QJSEngine()
    code = (RESOURCE_ROOT/'qml/SubjectTheme.js').read_text(encoding='utf-8').replace('.pragma library','')
    result = engine.evaluate(code)
    assert not result.isError(), result.toString()
    function = engine.globalObject().property('forSubject')
    def theme(subject):
        result = function.call([engine.toScriptValue(subject)])
        assert not result.isError(), result.toString()
        return result.toVariant()
    for subject in (*CURRICULUM_SUBJECTS, 'Tiếng Anh'):
        assert theme(subject)['id'] != 'general', subject
    assert theme('Vật lí')['id'] == theme('Vật lý')['id'] == 'physics'
    assert theme('Mỹ thuật')['id'] == theme('Mĩ thuật')['id'] == 'art'
    assert theme('Môn riêng')['id'] == 'general'
