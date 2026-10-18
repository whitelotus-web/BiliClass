import json
import subprocess
import sys
import threading
import time

import pytest

from app import office_tasks


def test_timeout_stops_only_the_child_we_started(tmp_path, monkeypatch):
    original = subprocess.Popen
    children = []

    def sleeping_child(command, **kwargs):
        process = original([sys.executable, '-c', 'import time; time.sleep(60)'], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(office_tasks.subprocess, 'Popen', sleeping_child)
    started = time.monotonic()
    with pytest.raises(office_tasks.OfficeTaskError, match='thời hạn'):
        office_tasks.run_task('render', tmp_path, {}, idle_timeout=.2, timeout=2)
    assert time.monotonic() - started < 5
    assert len(children) == 1 and children[0].poll() is not None


def test_cancel_stops_an_active_child(tmp_path, monkeypatch):
    original = subprocess.Popen
    children = []
    cancel = threading.Event()

    def sleeping_child(command, **kwargs):
        process = original([sys.executable, '-c', 'import time; time.sleep(60)'], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(office_tasks.subprocess, 'Popen', sleeping_child)
    timer = threading.Timer(.2, cancel.set)
    timer.start()
    try:
        with pytest.raises(InterruptedError):
            office_tasks.run_task('fit', tmp_path, {}, cancel, idle_timeout=3)
    finally:
        timer.cancel()
    assert children[0].poll() is not None


def test_completed_child_protocol_and_heartbeat(tmp_path, monkeypatch):
    original = subprocess.Popen
    code = '''import json,sys,time
from pathlib import Path
from app.library_location import write_record
p=Path(sys.argv[1])
for n in range(5):
    write_record(p/'progress.json', {'message':str(n)})
    time.sleep(.1)
(p/'result.json').write_text(json.dumps({'value':[1,2,3]}))
'''
    def child(command, **kwargs):
        return original([sys.executable, '-c', code, command[-1]], **kwargs)

    monkeypatch.setattr(office_tasks.subprocess, 'Popen', child)
    messages = []
    result = office_tasks.run_task('measure', tmp_path, {}, progress=messages.append,
                                    idle_timeout=1, timeout=5)
    assert result == [1, 2, 3] and messages


def test_native_crash_preserves_completed_slides_but_does_not_certify_others(tmp_path, monkeypatch):
    report = dict(sha256='original', slides=[
        dict(slide=1, issues=[], rendered=False), dict(slide=2, issues=[], rendered=False)])
    partial = dict(sha256='original', slides=[
        dict(slide=1, issues=[dict(code='text_overflow', severity='FAIL')], rendered=True),
        dict(slide=2, issues=[], rendered=False)])
    (tmp_path / 'partial.json').write_text(json.dumps(partial))
    def crash(*args, **kwargs):
        error = office_tasks.OfficeTaskError('RPC disconnected')
        error.folder = tmp_path
        raise error
    monkeypatch.setattr(office_tasks, 'run_task', crash)
    result = office_tasks.render_quality(tmp_path / 'source.pptx', tmp_path, report)
    assert result['slides'][0]['rendered']
    assert result['counts']['FAIL'] == 1
    assert not result['slides'][1]['rendered']
    assert any(i['code'] == 'render_unavailable' for i in result['slides'][1]['issues'])
