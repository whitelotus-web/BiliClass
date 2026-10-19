"""Explicit Windows taskbar identity, without an optional COM Python package."""

import ctypes
import os
import subprocess
import sys
from pathlib import Path

from .windows_com import Guid, apartment, check, method, release

APP_ID = 'BiliClass.Desktop'
PROPERTY_FORMAT = '9f4c2855-9f79-4b39-a8d0-e1d42de1d5f3'


def relaunch_properties(executable, *, frozen=True):
    from .paths import RESOURCE_ROOT

    executable = str(Path(executable).resolve())
    command = [executable] if frozen else [executable, '-m', 'app']
    icon = executable if frozen else str(RESOURCE_ROOT / 'assets/brand/biliclass.ico')
    # Windows refreshes grouping when ID is written; set relaunch data first.
    return [(2, subprocess.list2cmdline(command)), (4, 'BiliClass'), (3, icon + ',0'), (5, APP_ID)]


class _Key(ctypes.Structure):
    _fields_ = [('format', Guid), ('pid', ctypes.c_uint32)]


class _Value(ctypes.Union):
    _fields_ = [('text', ctypes.c_wchar_p), ('storage', ctypes.c_byte * (ctypes.sizeof(ctypes.c_void_p) * 2))]


class _Variant(ctypes.Structure):
    _fields_ = [('kind', ctypes.c_ushort), ('reserved', ctypes.c_ushort * 3), ('value', _Value)]


def _write_properties(target, properties, *, shortcut=False):
    shell = ctypes.WinDLL('shell32')
    with apartment():
        _write_store(shell, target, properties, shortcut=shortcut)


def _write_store(shell, target, properties, *, shortcut):
    store = ctypes.c_void_p()
    try:
        iid = Guid.parse('886d8eeb-8cf2-4446-8d02-cdba1dbdcf99')
        if shortcut:
            obtain = shell.SHGetPropertyStoreFromParsingName
            obtain.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(Guid), ctypes.POINTER(ctypes.c_void_p)]
            obtain.restype = ctypes.c_long
            check(obtain(str(target), None, 2, ctypes.byref(iid), ctypes.byref(store)))
        else:
            obtain = shell.SHGetPropertyStoreForWindow
            obtain.argtypes = [ctypes.c_void_p, ctypes.POINTER(Guid), ctypes.POINTER(ctypes.c_void_p)]
            obtain.restype = ctypes.c_long
            check(obtain(int(target), ctypes.byref(iid), ctypes.byref(store)))
        setter = method(store, 6, ctypes.POINTER(_Key), ctypes.POINTER(_Variant))
        for identity, text in properties:
            key = _Key(Guid.parse(PROPERTY_FORMAT), identity)
            value = _Variant()
            value.kind = 31  # VT_LPWSTR, held by ctypes until SetValue has copied it.
            value.value.text = text
            check(setter(store, ctypes.byref(key), ctypes.byref(value)))
        if shortcut:
            check(method(store, 7)(store))
            notify = shell.SHChangeNotify
            notify.argtypes = [ctypes.c_long, ctypes.c_uint32, ctypes.c_wchar_p, ctypes.c_void_p]
            notify.restype = None
            notify(0x2000, 0x2005, str(target), None)  # UPDATEITEM, PATHW | FLUSHNOWAIT.
    finally:
        release(store)


def configure_window(window):
    if os.name != 'nt':
        return
    _write_properties(int(window.winId()), relaunch_properties(sys.executable, frozen=getattr(sys, 'frozen', False)))


def register_shortcut(path):
    path = Path(path).resolve(strict=True)
    if path.name.casefold() != 'biliclass.lnk':
        raise ValueError('Chỉ đăng ký shortcut BiliClass.lnk.')
    if os.name != 'nt':
        raise OSError('Windows shortcuts require Windows.')
    _write_properties(path, [(5, APP_ID)], shortcut=True)
