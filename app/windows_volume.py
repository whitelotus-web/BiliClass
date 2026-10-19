"""Read/write the current Windows playback endpoint; never retain COM pointers."""

import ctypes

from .windows_com import Guid, apartment, check, method, release


def endpoint_volume(target=None):
    """Return (percent, muted); a deliberate positive adjustment unmutes output."""
    with apartment() as ole:
        enumerator, device, endpoint = (ctypes.c_void_p() for _ in range(3))
        try:
            clsid = Guid.parse('bcde0395-e52f-467c-8e3d-c4579291692e')
            iid = Guid.parse('a95664d2-9614-4f35-a746-de8db63617e6')
            ole.CoCreateInstance.argtypes = [ctypes.POINTER(Guid), ctypes.c_void_p, ctypes.c_uint32,
                                            ctypes.POINTER(Guid), ctypes.POINTER(ctypes.c_void_p)]
            ole.CoCreateInstance.restype = ctypes.c_long
            check(ole.CoCreateInstance(ctypes.byref(clsid), None, 23, ctypes.byref(iid), ctypes.byref(enumerator)))
            # eRender / eMultimedia: follows speakers, headphones and HDMI changes.
            check(method(enumerator, 4, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))(
                enumerator, 0, 1, ctypes.byref(device)))
            iid = Guid.parse('5cdf2c82-841e-4546-9722-0cf74078229a')
            check(method(device, 3, ctypes.POINTER(Guid), ctypes.c_uint32, ctypes.c_void_p,
                         ctypes.POINTER(ctypes.c_void_p))(device, ctypes.byref(iid), 23, None, ctypes.byref(endpoint)))
            if target is not None:
                target = max(0, min(100, int(target)))
                check(method(endpoint, 7, ctypes.c_float, ctypes.c_void_p)(endpoint, target / 100, None))
                if target > 0:
                    check(method(endpoint, 14, ctypes.c_int, ctypes.c_void_p)(endpoint, 0, None))
            scalar, muted = ctypes.c_float(), ctypes.c_int()
            check(method(endpoint, 9, ctypes.POINTER(ctypes.c_float))(endpoint, ctypes.byref(scalar)))
            check(method(endpoint, 15, ctypes.POINTER(ctypes.c_int))(endpoint, ctypes.byref(muted)))
            return round(scalar.value * 100), bool(muted.value)
        finally:
            for pointer in (endpoint, device, enumerator):
                release(pointer)
