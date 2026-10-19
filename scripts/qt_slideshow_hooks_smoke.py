"""Real input on two disposable windows, including signed HWND aliases."""

import queue
import time

import win32api
import win32con
import win32gui
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow

from app.slideshow_shortcuts import SlideshowKeys, window_identity
from scripts.qt_result_preview_mascot_smoke import pump, until


def main():
    app = QGuiApplication([])
    cursor = win32api.GetCursorPos()
    owned, other = QQuickWindow(), QQuickWindow()
    keys = SlideshowKeys()
    try:
        for index, window in enumerate((owned, other)):
            window.setTitle('BiliClass disposable hook verification')
            window.setFlags(Qt.Window | Qt.WindowStaysOnTopHint)
            window.setGeometry(180 + index * 380, 160, 320, 220)
            window.show()
            until(window.isExposed)
        hwnd = window_identity(int(owned.winId()))
        center = owned.mapToGlobal(QPoint(150, 100))
        keys.bind(hwnd - (1 << 32), 1289,
                  [('en', center.x()-35, center.y()-25, center.x()+35, center.y()+25)],
                  presenter=window_identity(int(other.winId())) - (1 << 32))
        keys.start()
        assert not keys.error, keys.error
        def click(window):
            target = window.mapToGlobal(QPoint(150, 100)).toTuple()
            assert window_identity(win32gui.GetAncestor(win32gui.WindowFromPoint(target), 2)) == window_identity(int(window.winId()))
            win32api.SetCursorPos(target)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            pump(30)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            pump(120)
        click(owned)
        assert keys.actions.get_nowait() == ('en', 1289)
        # Activate via title bar: the speaker click is consumed deliberately.
        owned.requestActivate()
        until(lambda: window_identity(win32gui.GetForegroundWindow()) == hwnd)
        win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
        pump(30)
        win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)
        pump(100)
        assert keys.actions.get_nowait() == ('en', 1289)
        keys.bind(hwnd - (1 << 32), 1289, keys._binding[2])
        click(other)
        until(lambda: window_identity(win32gui.GetForegroundWindow()) == window_identity(int(other.winId())))
        win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
        pump(30)
        win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)
        pump(100)
        try:
            unexpected = keys.actions.get_nowait()
        except queue.Empty:
            pass
        else:
            raise AssertionError(unexpected)
        print('PASS: signed HWND mouse/key input and unrelated-window pass-through', flush=True)
    finally:
        keys.close()
        owned.close()
        other.close()
        win32api.SetCursorPos(cursor)
        app.processEvents()
        time.sleep(.05)


if __name__ == '__main__':
    main()
