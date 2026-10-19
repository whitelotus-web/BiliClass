import multiprocessing
import os
import time
from pathlib import Path

import psutil
import pytest

from app.speech_process import RenderWorker


def fixture_worker(connection, root, threads):
    while True:
        request = connection.recv()
        if request is None:
            return
        text, voice, rate, temporary = request
        if text == 'crash':
            os._exit(9)
        if text == 'error':
            connection.send('Local fixture failure')
            continue
        time.sleep(.1)
        Path(temporary).write_text(text, encoding='utf-8')
        connection.send('')


def abruptly_exit_host(connection, directory):
    worker = RenderWorker(directory)
    worker._start()
    connection.send(worker.process.pid)
    connection.close()
    os._exit(0)


def test_model_helper_reuses_process_reports_failure_and_recovers_after_crash(tmp_path):
    worker = RenderWorker(tmp_path, target=fixture_worker)
    output = tmp_path / 'output.txt'
    try:
        worker.render('First lesson', 'voice', 0, output)
        identity = worker.process.pid
        assert identity != os.getpid() and output.read_text(encoding='utf-8') == 'First lesson'
        with pytest.raises(RuntimeError, match='Local fixture failure'):
            worker.render('error', 'voice', 0, output)
        assert worker.process.pid == identity
        with pytest.raises(RuntimeError, match='Bộ giọng đã dừng'):
            worker.render('crash', 'voice', 0, output)
        worker.process.join(3)
        worker.render('Next lesson', 'voice', 0, output)
        assert worker.process.pid != identity and output.read_text(encoding='utf-8') == 'Next lesson'
    finally:
        worker.stop()
    assert worker.process is None and worker.connection is None


def test_helper_exits_when_its_app_dies(tmp_path):
    context = multiprocessing.get_context('spawn')
    connection, child = context.Pipe()
    host = context.Process(target=abruptly_exit_host, args=(child, tmp_path))
    host.start()
    child.close()
    try:
        assert connection.poll(10)
        identity = connection.recv()
        host.join(5)
        assert not host.is_alive()
        try:
            helper = psutil.Process(identity)
        except psutil.NoSuchProcess:
            return  # Pipe EOF can let the idle helper exit before inspection.
        helper.wait(timeout=8)
        assert not helper.is_running()
    finally:
        connection.close()
        host.join(1)
