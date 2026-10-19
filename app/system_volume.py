"""Live master-volume state without Windows calls on the GUI thread."""

import os
from threading import Event, Lock, Thread
from weakref import ref

from PySide6.QtCore import QObject, Signal, Slot


class VolumeMonitor(Thread):
    def __init__(self, backend, publish):
        super().__init__(name='BiliClass system volume', daemon=True)
        self.backend, self.publish = backend, publish
        self.wake, self.stopping, self.lock = Event(), Event(), Lock()
        self.target = None
        self.revision = 0

    def request(self, value):
        with self.lock:
            self.target = value
            self.revision += 1
        self.wake.set()

    def stop(self):
        self.stopping.set()
        self.wake.set()

    def run(self):
        while not self.stopping.is_set():
            self.wake.clear()
            with self.lock:
                target, self.target = self.target, None
                revision = self.revision
            try:
                state = (*self.backend(target), True)
            except OSError:
                state = (target, False, False)
            if self.stopping.is_set():
                break
            try:
                if self.publish((revision, *state)) is False:
                    break
            except RuntimeError:  # The application was closed during a device call.
                break
            self.wake.wait(.6)


class SystemVolume(QObject):
    changed = Signal()
    sampled = Signal(int, object)

    def __init__(self, parent, backend=None):
        super().__init__(parent)
        if backend is None and os.name == 'nt':
            from .windows_volume import endpoint_volume

            backend = endpoint_volume
        self.backend = backend
        self.value, self.muted, self.available = 80, False, False
        self.worker = None
        self.generation = 0
        self.sampled.connect(self._receive)
        parent.destroyed.connect(self.shutdown)

    def activate(self, active):
        if active and self.backend and self.worker is None:
            self.generation += 1
            generation = self.generation
            reference = ref(self)
            def publish(state):
                owner = reference()
                if owner is None:
                    return False
                owner.sampled.emit(generation, state)
                return True
            self.worker = VolumeMonitor(self.backend, publish)
            self.worker.start()
        elif not active:
            self.shutdown()

    @Slot(int, object)
    def _receive(self, generation, state):
        if generation != self.generation or self.worker is None:
            return
        revision, value, muted, available = state
        if revision < self.worker.revision:
            return
        value = self.value if value is None else value
        if (value, muted, available) != (self.value, self.muted, self.available):
            self.value, self.muted, self.available = value, muted, available
            self.changed.emit()

    def set_value(self, value):
        if self.worker:
            value = max(0, min(100, int(value)))
            self.worker.request(value)
            if self.available and (value != self.value or self.muted):
                self.value, self.muted = value, False
                self.changed.emit()

    def shutdown(self):
        self.generation += 1
        if self.worker:
            self.worker.stop()
            self.worker = None
