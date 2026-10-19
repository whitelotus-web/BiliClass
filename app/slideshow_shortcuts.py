"""Validated narration keys and a fast, foreground-scoped Windows input hook.

The hook never calls Office, reads files or synthesizes speech. It queues only
configured actions for the exact slideshow window; all other input passes on.
"""

import ctypes
import queue
import sys
import threading
from ctypes import wintypes

DEFAULTS = {'en': 'Space', 'vi': 'Enter', 'both': 'Ctrl+Space'}
KEYS = {'Space': 0x20, 'Enter': 0x0D}
KEYS.update({chr(key): key for key in range(65, 91)})
KEYS.update({str(key): 48 + key for key in range(10)})
KEYS.update({f'F{number}': 0x6F + number for number in range(1, 13) if number != 5})
MODIFIERS = {'Ctrl': 1, 'Alt': 2, 'Shift': 4}


def validate(bindings):
    if not isinstance(bindings, dict) or set(bindings) != set(DEFAULTS):
        raise ValueError('Cần gán đủ ba phím đọc Anh, Việt và hai ngôn ngữ.')
    result = {}
    for language in DEFAULTS:
        sequence = bindings[language]
        if not isinstance(sequence, str):
            raise ValueError('Phím đọc không hợp lệ.')
        parts = sequence.split('+')
        count = 2 if language == 'both' else 1
        if len(parts) != count or parts[-1] not in KEYS or (count == 2 and parts[0] not in MODIFIERS):
            raise ValueError('Anh và Việt dùng một phím; hai ngôn ngữ dùng Ctrl/Alt/Shift cùng một phím. Esc, F5 và các phím điều hướng được giữ cho PowerPoint.')
        if sequence in {'Alt+F4', 'Alt+Space', 'Ctrl+Esc', 'Ctrl+F4'}:
            raise ValueError('Tổ hợp này dành cho cửa sổ Windows. Hãy chọn phím khác.')
        result[language] = sequence
    if len(set(result.values())) != len(result):
        raise ValueError('Các chức năng đọc phải dùng phím khác nhau.')
    return result


def saved_bindings(value):
    try:
        return validate(value)
    except ValueError:
        return dict(DEFAULTS)


def display(sequence):
    return sequence.replace('Space', 'Space ␣').replace('Enter', 'Enter ↵').replace('+', ' + ')


class KeyPolicy:
    """Pure input policy, independent of Windows and Office for contract tests."""

    def __init__(self, bindings=None):
        self.bindings = saved_bindings(bindings)
        self.held = set()

    def key(self, vk, modifiers, down, focused):
        if not focused:
            self.held.discard(vk)
            return False, None
        if not down:
            if vk in self.held:
                self.held.remove(vk)
                return True, None
            return False, None
        if vk in self.held:
            return True, None  # Holding a key must not repeatedly pause/resume.
        for language, sequence in self.bindings.items():
            parts = sequence.split('+')
            wanted = MODIFIERS[parts[0]] if len(parts) == 2 else 0
            if vk == KEYS[parts[-1]] and modifiers == wanted:
                self.held.add(vk)
                return True, language
        if modifiers == 0 and vk in {0x26, 0x28}:
            self.held.add(vk)
            return True, 'volume_up' if vk == 0x26 else 'volume_down'
        return False, None


class SlideshowKeys:
    """One hook thread owned by the disposable Office helper, with bounded stop."""

    def __init__(self, bindings=None):
        self.policy = KeyPolicy(bindings)
        self._binding = (0, 0, (), frozenset())
        self.actions = queue.SimpleQueue()
        self.stopping = threading.Event()
        self.ready = threading.Event()
        self.error = ''
        self.thread = None

    def configure(self, bindings):
        self.policy.bindings = validate(bindings)

    def bind(self, hwnd=0, slide_id=0, regions=(), presenter=0):
        # Publish one immutable snapshot: callbacks cannot see a new slide ID
        # paired with a previous slide's click regions or presenter window.
        self._binding = (hwnd, slide_id, tuple(regions),
                         frozenset(handle for handle in (hwnd, presenter) if handle))

    def start(self):
        if sys.platform != 'win32':
            self.error = 'Phím đọc trình chiếu cần Windows.'
            return
        self.thread = threading.Thread(target=self._guarded_run, name='BiliClass slideshow keys', daemon=True)
        self.thread.start()
        self.ready.wait(2)
        if not self.ready.is_set():
            self.error = 'Chưa chuẩn bị xong phím đọc. Dùng nút đọc trên Mascot.'

    def close(self):
        self.bind()
        self.stopping.set()
        if self.thread:
            self.thread.join(2)

    def _guarded_run(self):
        try:
            self._run()
        except Exception:
            self.error = 'Chưa bật được phím đọc. Dùng nút đọc trên Mascot.'
            self.ready.set()

    def _run(self):
        user = ctypes.WinDLL('user32', use_last_error=True)
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, ctypes.c_size_t, ctypes.c_ssize_t)

        class Keyboard(ctypes.Structure):
            _fields_ = [('vkCode', wintypes.DWORD), ('scanCode', wintypes.DWORD),
                        ('flags', wintypes.DWORD), ('time', wintypes.DWORD), ('extra', ctypes.c_size_t)]

        class Mouse(ctypes.Structure):
            _fields_ = [('point', wintypes.POINT), ('mouseData', wintypes.DWORD),
                        ('flags', wintypes.DWORD), ('time', wintypes.DWORD), ('extra', ctypes.c_size_t)]

        user.SetWindowsHookExW.argtypes = [ctypes.c_int, callback_type, wintypes.HINSTANCE, wintypes.DWORD]
        user.SetWindowsHookExW.restype = wintypes.HHOOK
        user.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, ctypes.c_size_t, ctypes.c_ssize_t]
        user.CallNextHookEx.restype = ctypes.c_ssize_t
        user.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
        user.GetForegroundWindow.restype = wintypes.HWND
        user.WindowFromPoint.argtypes = [wintypes.POINT]
        user.WindowFromPoint.restype = wintypes.HWND
        user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        user.GetAncestor.restype = wintypes.HWND
        user.GetAsyncKeyState.argtypes = [ctypes.c_int]
        user.GetAsyncKeyState.restype = ctypes.c_short
        user.MsgWaitForMultipleObjects.argtypes = [wintypes.DWORD, ctypes.c_void_p, wintypes.BOOL, wintypes.DWORD, wintypes.DWORD]
        user.MsgWaitForMultipleObjects.restype = wintypes.DWORD
        kernel.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel.GetModuleHandleW.restype = wintypes.HMODULE

        def handle(code, message, data):
            if code >= 0 and message in {0x100, 0x101, 0x104, 0x105}:
                key = ctypes.cast(data, ctypes.POINTER(Keyboard)).contents
                hwnd, slide_id, _, focus_windows = self._binding
                focused = user.GetForegroundWindow() in focus_windows
                modifiers = sum(mask for vk, mask in ((0x11, 1), (0x12, 2), (0x10, 4))
                                if user.GetAsyncKeyState(vk) & 0x8000)
                # Win+key belongs to Windows, even if the base key is configured.
                if any(user.GetAsyncKeyState(vk) & 0x8000 for vk in (0x5B, 0x5C)):
                    focused = False
                consumed, language = self.policy.key(key.vkCode, modifiers, message in {0x100, 0x104}, focused)
                if language:
                    self.actions.put((language, slide_id))
                if consumed:
                    return 1
            return user.CallNextHookEx(None, code, message, data)

        def guarded(callback, code, message, data):
            try:
                return callback(code, message, data)
            except Exception:
                return user.CallNextHookEx(None, code, message, data)

        callback = callback_type(lambda *args: guarded(handle, *args))  # Retain until after unhook.
        mouse_held = False

        def mouse_handle(code, message, data):
            nonlocal mouse_held
            if code >= 0 and message in {0x201, 0x202}:  # Only left-button down/up.
                point = ctypes.cast(data, ctypes.POINTER(Mouse)).contents.point
                hwnd, slide_id, regions, _ = self._binding
                focused = bool(hwnd and user.GetForegroundWindow() == hwnd and
                               user.GetAncestor(user.WindowFromPoint(point), 2) == hwnd)
                if message == 0x202:
                    held, mouse_held = mouse_held, False
                    if held:
                        return 1
                elif focused:
                    for language, left, top, right, bottom in regions:
                        if left <= point.x < right and top <= point.y < bottom:
                            mouse_held = True
                            self.actions.put((language, slide_id))
                            return 1
            return user.CallNextHookEx(None, code, message, data)

        mouse_callback = callback_type(lambda *args: guarded(mouse_handle, *args))
        hook = user.SetWindowsHookExW(13, callback, kernel.GetModuleHandleW(None), 0)
        mouse_hook = user.SetWindowsHookExW(14, mouse_callback, kernel.GetModuleHandleW(None), 0)
        if not hook:
            self.error = 'Chưa bật được phím đọc. Dùng loa hoặc nút đọc trên Mascot.'
        elif not mouse_hook:
            self.error = 'Chưa bật được bấm loa để tạm dừng. Dùng nút đọc trên Mascot.'
        self.ready.set()
        if not hook and not mouse_hook:
            return
        try:
            message = wintypes.MSG()
            while not self.stopping.is_set():
                while user.PeekMessageW(ctypes.byref(message), None, 0, 0, 1):
                    user.TranslateMessage(ctypes.byref(message))
                    user.DispatchMessageW(ctypes.byref(message))
                # Wake immediately for input, rather than polling at 125 Hz
                # while idle. The timeout bounds shutdown without GUI input.
                user.MsgWaitForMultipleObjects(0, None, False, 50, 0x04FF)  # QS_ALLINPUT
        finally:
            if hook:
                user.UnhookWindowsHookEx(hook)
            if mouse_hook:
                user.UnhookWindowsHookEx(mouse_hook)
