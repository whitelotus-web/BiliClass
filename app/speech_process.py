"""Persistent local TTS helpers: native model initialization cannot hold Qt's GIL."""

import multiprocessing
import os
from threading import Event, Lock, Thread


def worker_main(connection, root, threads):
    from . import speech

    parent = multiprocessing.parent_process()
    stopped = Event()

    def watch_parent():
        while not stopped.wait(1):
            if parent is not None and not parent.is_alive():
                os._exit(0)  # Only this private model helper; no user document is open.

    Thread(target=watch_parent, name='bcl-voice-parent', daemon=True).start()
    os.environ['BILICLASS_VIENEU_DIR'] = root
    speech._SYNTHESIS_CONTEXT.worker_threads = threads
    try:
        while True:
            request = connection.recv()
            if request is None:
                return
            try:
                speech._synthesize_vieneu_local(*request)
                connection.send('')
            except Exception as exc:
                connection.send(str(exc)[:500] or type(exc).__name__)
    except (EOFError, OSError):
        pass
    finally:
        stopped.set()
        connection.close()


class RenderWorker:
    def __init__(self, root, threads=4, *, target=worker_main):
        self.root, self.threads, self.target = str(root), threads, target
        self.lock = Lock()
        self.process = self.connection = None

    def _start(self):
        context = multiprocessing.get_context('spawn')
        connection, child = context.Pipe()
        process = context.Process(target=self.target, args=(child, self.root, self.threads),
                                  name='BiliClass-voice', daemon=True)
        try:
            process.start()
        except Exception:
            connection.close()
            raise
        finally:
            child.close()
        self.connection, self.process = connection, process

    def render(self, text, voice, rate, temporary):
        with self.lock:
            if self.process is not None and not self.process.is_alive():
                self.connection.close()
                self.process.close()
                self.process = self.connection = None
            if self.process is None:
                self._start()
            try:
                self.connection.send((text, voice, rate, temporary))
                while not self.connection.poll(.1):
                    if not self.process.is_alive():
                        raise EOFError()
                error = self.connection.recv()
            except (EOFError, OSError) as exc:
                raise RuntimeError('Bộ giọng đã dừng. Bài giảng vẫn được lưu; bấm Tạo giọng đọc để tiếp tục.') from exc
            if error:
                raise RuntimeError(error)

    def stop(self):
        if not self.lock.acquire(timeout=.1):
            return  # The caller joins narration first; never interrupt a live inference.
        try:
            if self.connection is not None:
                try:
                    self.connection.send(None)
                except (EOFError, OSError):
                    pass
                self.connection.close()
                self.connection = None
            if self.process is not None:
                self.process.join(2)
                if not self.process.is_alive():
                    self.process.close()
                    self.process = None
        finally:
            self.lock.release()


_workers = {}
_lock = Lock()


def render(root, text, voice, rate, temporary, *, secondary=False):
    key = str(root), secondary
    with _lock:
        if key not in _workers:
            _workers[key] = RenderWorker(root, 2 if secondary else 4)
        worker = _workers[key]
    worker.render(text, voice, rate, temporary)


def release_secondary():
    with _lock:
        for key in [key for key in _workers if key[1]]:
            _workers.pop(key).stop()


def shutdown():
    with _lock:
        workers = list(_workers.values())
        _workers.clear()
    for worker in workers:
        worker.stop()
