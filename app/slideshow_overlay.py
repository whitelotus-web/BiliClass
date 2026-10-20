"""Non-activating speaker artwork owned by the exact slideshow window.

Changing a slide shape during a show can redraw/reset its animation builds.
These tiny transparent windows change artwork without editing the live deck.
Mouse input passes through to the existing, slideshow-scoped input hook.
"""

import ctypes
import io
import struct
from ctypes import wintypes
from functools import lru_cache

from PIL import Image, ImageChops

from .speaker_artwork import artwork


@lru_cache(maxsize=32)
def pixels(language, paused, width, height):
    data, crop = artwork(language, paused=paused)
    with Image.open(io.BytesIO(data)) as source:
        image = source.convert('RGBA')
    if crop:
        w, h = image.size
        image = image.crop((round(int(crop['l']) * w / 100000), round(int(crop['t']) * h / 100000),
                            round(w * (1 - int(crop['r']) / 100000)),
                            round(h * (1 - int(crop['b']) / 100000))))
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    fitted = Image.new('RGBA', (width, height))
    fitted.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    r, g, b, alpha = fitted.split()
    return Image.merge('RGBA', (ImageChops.multiply(r, alpha), ImageChops.multiply(g, alpha),
                               ImageChops.multiply(b, alpha), alpha)).tobytes('raw', 'BGRA')


class SpeakerOverlay:
    def __init__(self):
        import win32api
        import win32gui

        self.gui = win32gui
        self.instance = win32api.GetModuleHandle(None)
        self.class_name = 'BiliClass.Speakers.' + str(id(self))
        self.windows = {}
        self.last = None
        self.gdi = ctypes.WinDLL('gdi32', use_last_error=True)
        self.gdi.CreateCompatibleDC.argtypes = [wintypes.HDC]
        self.gdi.CreateCompatibleDC.restype = wintypes.HDC
        self.gdi.CreateDIBSection.argtypes = [wintypes.HDC, ctypes.c_void_p, wintypes.UINT,
                                            ctypes.POINTER(ctypes.c_void_p), wintypes.HANDLE, wintypes.DWORD]
        self.gdi.CreateDIBSection.restype = wintypes.HBITMAP
        self.gdi.SelectObject.argtypes = [wintypes.HDC, wintypes.HANDLE]
        self.gdi.SelectObject.restype = wintypes.HANDLE
        self.gdi.DeleteObject.argtypes = [wintypes.HANDLE]
        self.gdi.DeleteDC.argtypes = [wintypes.HDC]
        window_class = win32gui.WNDCLASS()
        window_class.hInstance = self.instance
        window_class.lpszClassName = self.class_name
        window_class.lpfnWndProc = self._message
        win32gui.RegisterClass(window_class)
        try:
            for language in ('vi', 'en', 'both'):
                # WS_EX_LAYERED | TRANSPARENT | TOOLWINDOW | NOACTIVATE.
                self.windows[language] = self._window()
                self._paint(self.windows[language], (0, 0, 28, 28), pixels(language, False, 28, 28))
        except Exception:
            self.close()
            raise

    def _message(self, hwnd, message, wparam, lparam):
        if message == 0x84:  # WM_NCHITTEST: never swallow a slide click.
            return -1
        if message == 0x21:  # WM_MOUSEACTIVATE: never steal keyboard focus.
            return 3
        return self.gui.DefWindowProc(hwnd, message, wparam, lparam)

    def _window(self):
        # Disabled artwork is also ignored by WindowFromPoint in the input hook.
        return self.gui.CreateWindowEx(0x080800A0, self.class_name, '', 0x88000000,
                                       0, 0, 1, 1, 0, 0, self.instance, None)

    def _paint(self, hwnd, box, data):
        left, top, width, height = box
        screen = self.gui.GetDC(0)
        dc = bitmap = old = None
        try:
            dc = self.gdi.CreateCompatibleDC(screen)
            info = ctypes.create_string_buffer(struct.pack('<IiiHHIIiiII', 40, width, -height, 1,
                                                          32, 0, width * height * 4, 0, 0, 0, 0))
            bits = ctypes.c_void_p()
            bitmap = self.gdi.CreateDIBSection(screen, info, 0, ctypes.byref(bits), None, 0)
            if not dc or not bitmap or not bits.value:
                raise ctypes.WinError(ctypes.get_last_error())
            ctypes.memmove(bits, data, len(data))
            old = self.gdi.SelectObject(dc, bitmap)
            self.gui.UpdateLayeredWindow(hwnd, screen, (left, top), (width, height), dc, (0, 0),
                                         0, (0, 0, 255, 1), 2)
        finally:
            if old:
                self.gdi.SelectObject(dc, old)
            if bitmap:
                self.gdi.DeleteObject(bitmap)
            if dc:
                self.gdi.DeleteDC(dc)
            self.gui.ReleaseDC(0, screen)

    def update(self, owner=0, regions=(), playing=()):
        regions = tuple(regions)
        visible = bool(owner and self.gui.IsWindow(owner) and self.gui.IsWindowVisible(owner)
                       and not self.gui.IsIconic(owner))
        state = (owner, visible, regions, frozenset(playing))
        if state == self.last:
            return
        shown = set()
        if visible:
            for language, left, top, right, bottom in regions:
                hwnd = self.windows.get(language)
                if not hwnd:
                    continue
                if not self.gui.IsWindow(hwnd):
                    hwnd = self.windows[language] = self._window()
                width, height = max(1, round(right - left)), max(1, round(bottom - top))
                self.gui.SetWindowLong(hwnd, -8, owner)  # Owned by this show, never globally topmost.
                self._paint(hwnd, (round(left), round(top), width, height),
                            pixels(language, language in playing, width, height))
                self.gui.SetWindowPos(hwnd, 0, round(left), round(top), width, height, 0x0054)
                shown.add(language)  # SWP_NOACTIVATE | NOZORDER | SHOWWINDOW.
        for language, hwnd in self.windows.items():
            if language not in shown and self.gui.IsWindow(hwnd):
                self.gui.ShowWindow(hwnd, 0)
        self.last = state

    def close(self):
        for hwnd in self.windows.values():
            if self.gui.IsWindow(hwnd):
                self.gui.DestroyWindow(hwnd)
        self.windows.clear()
        self.gui.UnregisterClass(self.class_name, self.instance)
