"""Small COM ABI helpers for Windows shell and Core Audio interfaces."""

import ctypes
from contextlib import contextmanager
from uuid import UUID


class Guid(ctypes.Structure):
    _fields_ = [('data1', ctypes.c_uint32), ('data2', ctypes.c_uint16),
               ('data3', ctypes.c_uint16), ('data4', ctypes.c_ubyte * 8)]

    @classmethod
    def parse(cls, value):
        return cls.from_buffer_copy(UUID(value).bytes_le)


def check(result):
    if result < 0:
        raise OSError('Windows COM HRESULT ' + hex(result & 0xffffffff))


@contextmanager
def apartment():
    ole = ctypes.WinDLL('ole32')
    ole.CoInitializeEx.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    ole.CoInitializeEx.restype = ctypes.c_long
    result = ole.CoInitializeEx(None, 2)
    if result & 0xffffffff != 0x80010106:  # An existing MTA is also usable.
        check(result)
    try:
        yield ole
    finally:
        if result >= 0:
            ole.CoUninitialize()


def method(pointer, index, *arguments):
    table = ctypes.cast(pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *arguments)(table[index])


def release(pointer):
    if pointer.value:
        method(pointer, 2)(pointer)
