"""Bound the loaded BLAS pools without reopening DLLs by filename on Windows."""

import ctypes
import os
from contextlib import contextmanager


def _blas_controls():
    """Resolve OpenBLAS controls from live module handles (Unicode-safe)."""
    from ctypes.wintypes import DWORD, HANDLE, HMODULE

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.GetCurrentProcess.restype = HANDLE
    kernel.GetProcAddress.argtypes = [HMODULE, ctypes.c_char_p]
    kernel.GetProcAddress.restype = ctypes.c_void_p
    psapi.EnumProcessModulesEx.argtypes = [HANDLE, ctypes.POINTER(HMODULE), DWORD,
                                         ctypes.POINTER(DWORD), DWORD]
    psapi.EnumProcessModulesEx.restype = ctypes.c_int
    required, count = DWORD(), 256
    while True:
        modules = (HMODULE * count)()
        if not psapi.EnumProcessModulesEx(kernel.GetCurrentProcess(), modules, ctypes.sizeof(modules),
                                         ctypes.byref(required), 3):
            raise ctypes.WinError(ctypes.get_last_error())
        if required.value <= ctypes.sizeof(modules):
            break
        count = required.value // ctypes.sizeof(HMODULE) + 32
    controls = []
    for module in modules[:required.value // ctypes.sizeof(HMODULE)]:
        for prefix, suffix in (("", ""), ("", "64_"), ("scipy_", ""), ("scipy_", "64_")):
            get = kernel.GetProcAddress(module, f"{prefix}openblas_get_num_threads{suffix}".encode("ascii"))
            set_ = kernel.GetProcAddress(module, f"{prefix}openblas_set_num_threads{suffix}".encode("ascii"))
            if get and set_:
                controls.append((module, ctypes.CFUNCTYPE(ctypes.c_int)(get),
                                 ctypes.CFUNCTYPE(None, ctypes.c_int)(set_)))
                break
    return controls


@contextmanager
def blas_budget():
    if os.name != "nt":
        from threadpoolctl import threadpool_limits

        with threadpool_limits(limits=1, user_api="blas"):
            yield
        return
    # Reopening the filename reported by Windows' module snapshot can fail
    # in a frozen app installed in a Vietnamese directory. The loaded DLL
    # already exposes these controls; no path conversion or reload is needed.
    saved = []
    try:
        for _, get, set_ in _blas_controls():
            saved.append((set_, get()))
            set_(1)
        yield
    finally:
        for set_, previous in reversed(saved):
            set_(previous)
