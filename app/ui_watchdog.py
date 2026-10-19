"""Local stack evidence for intermittent GUI stalls; no user text or locals."""

import os
import sys
from threading import Event, Lock, Thread, get_ident
from time import monotonic

from PySide6.QtCore import QTimer


class UiWatchdog:
    def __init__(self, app, directory, *, timeout=5, interval=1):
        self.path = directory / 'logs' / ('ui-hang-' + str(os.getpid()) + '.log')
        self.timeout, self.interval = timeout, interval
        self._stopped, self._lock = Event(), Lock()
        self._heartbeat = monotonic()
        self._reported = False
        self._main_thread = get_ident()
        self.timer = QTimer(app)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.beat)
        app.aboutToQuit.connect(self.stop)
        # The native faulthandler watchdog walks live CPython frames without
        # the GIL. That diagnostic itself crashed the packaged 3.12 runtime.
        # A Python thread takes strong frame/code references while holding the
        # GIL instead. A GIL stall can delay a report, never justify unsafe reads.
        self.thread = Thread(target=self._monitor, name='bcl-ui-watchdog', daemon=True)
        self.thread.start()
        self.timer.start()

    def beat(self):
        with self._lock:
            self._heartbeat = monotonic()
            self._reported = False

    def _monitor(self):
        while not self._stopped.wait(self.interval):
            with self._lock:
                elapsed = monotonic() - self._heartbeat
                report = elapsed >= self.timeout and not self._reported
                if report:
                    self._reported = True
            if report:
                self._report(elapsed)

    def _report(self, elapsed):
        lines = [f'GUI heartbeat delayed: {elapsed:.2f}s\n']
        frames = sys._current_frames()
        try:
            for identity, frame in frames.items():
                if identity == get_ident():
                    continue
                marker = ' (GUI)' if identity == self._main_thread else ''
                lines.append(f'Thread 0x{identity:x}{marker}:\n')
                for _ in range(100):
                    code = frame.f_code
                    lines.append(f'  File "{code.co_filename}", line {frame.f_lineno} in {code.co_name}\n')
                    frame = frame.f_back
                    if frame is None:
                        break
        finally:
            frames.clear()
        try:
            # All file I/O belongs to this monitor, including close. A slow
            # disk or shutdown must not block the GUI or close a live writer.
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open('a', encoding='utf-8') as output:
                output.writelines(lines)
        except OSError:
            pass  # Optional diagnostics cannot take down the application.

    def stop(self):
        self.timer.stop()
        self._stopped.set()
