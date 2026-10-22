"""A small separate Qt process keeps startup animation independent of loading."""

import json
import os
import subprocess
import sys
from queue import Empty, SimpleQueue
from threading import Thread

STAGES = {'preparing', 'library', 'interface', 'ready'}


def reduced_motion():
    if os.name == 'nt':
        import ctypes

        enabled = ctypes.c_int(1)
        if ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0):
            return not enabled.value  # Windows: animate controls and elements.
    return False


def input_stream():
    if sys.stdin is not None:
        return sys.stdin
    if os.name == 'nt':
        # Windowed Python/PyInstaller can omit sys.stdin even with a valid
        # inherited pipe. Read that explicit handle, never a console window.
        import ctypes
        import msvcrt
        from ctypes import wintypes

        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel.GetStdHandle.restype = wintypes.HANDLE
        handle = kernel.GetStdHandle(-10)
        if handle and handle != ctypes.c_void_p(-1).value:
            return os.fdopen(msvcrt.open_osfhandle(handle, os.O_RDONLY), 'r', encoding='utf-8')
    return None


class StartupSplash:
    def __init__(self, process=None):
        self.process, self.closed = process, False

    def stage(self, value):
        if self.closed or self.process is None or value not in STAGES:
            return
        try:
            self.process.stdin.write(json.dumps({'stage': value}) + '\n')
            self.process.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            self.close()

    def finish(self):
        if not self.closed:
            self.stage('ready')
            self.close()

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.process is None:
            return
        try:
            self.process.stdin.close()
        except (BrokenPipeError, OSError, ValueError):
            pass
        # Never wait for another process on the desktop's GUI thread.
        process = self.process

        def reap():
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    process.terminate()  # Only our dedicated, data-free splash.
                    process.wait(timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass

        Thread(target=reap, name='bcl-splash-close', daemon=True).start()


def start(enabled=True):
    if not enabled:
        return StartupSplash()
    command = [sys.executable]
    if not getattr(sys, 'frozen', False):
        command += ['-m', 'app']
    command += ['--startup-splash']
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, text=True, encoding='utf-8', close_fds=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except OSError:
        return StartupSplash()  # An optional loading screen cannot block the app.
    return StartupSplash(process)


def run():
    from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal
    from PySide6.QtGui import QCursor, QFont, QFontDatabase, QGuiApplication, QIcon
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuickControls2 import QQuickStyle

    from .paths import RESOURCE_ROOT

    app = QGuiApplication([])
    app.setApplicationName('BiliClass')
    app.setWindowIcon(QIcon(str(RESOURCE_ROOT/'assets/brand/biliclass.png')))
    QQuickStyle.setStyle('Basic')
    for path in (RESOURCE_ROOT/'assets').glob('BeVietnamPro-*.ttf'):
        QFontDatabase.addApplicationFont(str(path))
    app.setFont(QFont('Be Vietnam Pro', 10))

    class State(QObject):
        changed = Signal()

        def __init__(self):
            super().__init__()
            self.value = 'preparing'

        @Property(bool, constant=True)
        def reducedMotion(self):
            return motion_reduced

        @Property(str, notify=changed)
        def stage(self):
            return self.value

        def update(self, value):
            if value in STAGES and value != self.value:
                self.value = value
                self.changed.emit()

    motion_reduced = reduced_motion()
    state, inbox = State(), SimpleQueue()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty('splashState', state)
    engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/StartupSplash.qml')))
    if not engine.rootObjects():
        return 1
    window = engine.rootObjects()[0]
    screen = app.screenAt(QCursor.pos()) or app.primaryScreen()
    area = screen.availableGeometry()
    width = min(window.width(), int(area.width()*.82), int(area.height()*.82*1672/941))
    window.resize(width, round(width*941/1672))
    window.setPosition(area.x()+(area.width()-window.width())//2,
                       area.y()+(area.height()-window.height())//2)

    def read():
        try:
            stream = input_stream()
            if stream is None:
                return
            for line in stream:
                if len(line) > 1024:
                    break
                try:
                    value = json.loads(line)
                    inbox.put(value.get('stage') if isinstance(value, dict) else '')
                except (ValueError, TypeError):
                    pass
        except (OSError, AttributeError):
            pass
        finally:
            inbox.put(None)  # EOF also closes the splash if the parent fails.

    Thread(target=read, name='bcl-splash-pipe', daemon=True).start()

    def receive():
        for _ in range(20):
            try:
                value = inbox.get_nowait()
            except Empty:
                break
            if value is None:
                if state.value != 'ready':
                    app.quit()
                break
            if value in STAGES:
                state.update(value)
                if value == 'ready':
                    QTimer.singleShot(0 if motion_reduced else 120, app.quit)

    timer = QTimer(app)
    timer.setInterval(20)
    timer.timeout.connect(receive)
    timer.start()
    window.show()
    return app.exec()
