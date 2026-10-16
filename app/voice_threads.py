"""Bound the loaded BLAS pools without reopening DLLs by filename on Windows."""

import ctypes
import os
from contextlib import contextmanager
from threading import RLock

_BUDGET_LOCK = RLock()
_BUDGET_USERS = 0
_BUDGET_RESTORE = None


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
    global _BUDGET_USERS, _BUDGET_RESTORE
    # BLAS limits affect the process, not a Python thread. Two active engines
    # must share the limit until the last one exits, including error paths.
    with _BUDGET_LOCK:
        if not _BUDGET_USERS:
            if os.name != 'nt':
                from threadpoolctl import threadpool_limits
                context=threadpool_limits(limits=1,user_api='blas')
                context.__enter__()
                _BUDGET_RESTORE=lambda: context.__exit__(None,None,None)
            else:
                saved=[]
                try:
                    for _,get,set_ in _blas_controls():
                        saved.append((set_,get()))
                        set_(1)
                except BaseException:
                    for set_,previous in reversed(saved):
                        set_(previous)
                    raise
                def restore():
                    for setter,previous in reversed(saved):
                        setter(previous)
                _BUDGET_RESTORE=restore
        _BUDGET_USERS+=1
    try:
        yield
    finally:
        with _BUDGET_LOCK:
            _BUDGET_USERS-=1
            if not _BUDGET_USERS:
                restore,_BUDGET_RESTORE=_BUDGET_RESTORE,None
                restore()
