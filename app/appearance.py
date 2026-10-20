"""Application appearance helpers; presentation content is never recolored."""
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

MODES = frozenset({'light', 'dark'})


def saved_mode(library):
    value = library.setting('application_theme', 'light')
    return value if isinstance(value, str) and value in MODES else 'light'


def apply_color_scheme(mode):
    application = QGuiApplication.instance()
    if isinstance(application, QGuiApplication):
        application.styleHints().setColorScheme(Qt.ColorScheme.Dark if mode == 'dark' else Qt.ColorScheme.Light)


def apply_window(window, mode):
    if os.name != 'nt' or not window:
        return
    import ctypes
    from ctypes import wintypes

    dark = wintypes.BOOL(mode == 'dark')
    # The system caption buttons must follow the same mode as the QML title bar.
    setter = ctypes.windll.dwmapi.DwmSetWindowAttribute
    setter.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
    setter.restype = ctypes.c_long
    setter(int(window.winId()), 20, ctypes.byref(dark), ctypes.sizeof(dark))
