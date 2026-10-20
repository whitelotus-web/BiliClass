import json
import sys
import time
from threading import Event
from types import SimpleNamespace

import pytest

from app import startup_splash


def test_disabled_splash_never_starts_another_process(monkeypatch):
    monkeypatch.setattr(startup_splash.subprocess, 'Popen', lambda *a, **k: pytest.fail('Unexpected child'))
    screen = startup_splash.start(False)
    screen.stage('library')
    screen.finish()
    assert screen.closed


def test_finishing_splash_never_waits_on_the_gui_thread():
    release, waiting, writes = Event(), Event(), []
    pipe = SimpleNamespace(write=writes.append, flush=lambda: None, close=lambda: None)

    def wait(timeout):
        waiting.set()
        release.wait(2)

    process = SimpleNamespace(stdin=pipe, wait=wait)
    screen = startup_splash.StartupSplash(process)
    try:
        start = time.monotonic()
        screen.stage('interface')
        screen.finish()
        assert time.monotonic()-start < .2
        assert waiting.wait(.5)
        screen.close()
        assert [json.loads(value)['stage'] for value in writes] == ['interface', 'ready']
    finally:
        release.set()


def test_missing_splash_executable_cannot_prevent_desktop_startup(monkeypatch):
    def fail(*a, **k):
        raise OSError('No optional window')
    monkeypatch.setattr(startup_splash.subprocess, 'Popen', fail)
    screen = startup_splash.start()
    screen.finish()
    assert screen.closed and screen.process is None


def test_smoke_route_disables_splash_and_closes_it_even_on_failure(monkeypatch):
    from app.__main__ import main

    enabled, closed = [], []
    screen = SimpleNamespace(close=lambda: closed.append(True))
    monkeypatch.setattr(startup_splash, 'start', lambda **kw: enabled.append(kw['enabled']) or screen)
    monkeypatch.setattr(sys, 'argv', ['BiliClass', '--smoke'])

    def fail(args):
        assert args.startup_screen is screen
        raise ValueError('Fixture failure')

    monkeypatch.setitem(sys.modules, 'app.ui', SimpleNamespace(run=fail))
    with pytest.raises(ValueError, match='Fixture failure'):
        main()
    assert enabled == [False] and closed == [True]


def test_office_worker_route_never_opens_splash(monkeypatch):
    from app.__main__ import main

    monkeypatch.setattr(startup_splash, 'start', lambda *a, **k: pytest.fail('Worker opened splash'))
    monkeypatch.setitem(sys.modules, 'app.office_tasks', SimpleNamespace(worker_main=lambda value: 17))
    monkeypatch.setattr(sys, 'argv', ['BiliClass', '--office-task', 'fixture'])
    assert main() == 17
