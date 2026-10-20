"""Own processes/windows only: real splash animation, IPC, EOF and first frame."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import psutil
import win32gui
import win32process
import win32ui
from PIL import Image, ImageChops

from app.startup_splash import StartupSplash


def windows(process):
    identities = {process.pid}
    try:
        identities.update(child.pid for child in psutil.Process(process.pid).children(recursive=True))
    except psutil.Error:
        pass
    found = []
    def collect(hwnd, _):
        if win32process.GetWindowThreadProcessId(hwnd)[1] in identities and win32gui.IsWindowVisible(hwnd):
            found.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(collect, None)
    return found


def until(action, timeout=20):
    end = time.monotonic()+timeout
    while time.monotonic() < end:
        value = action()
        if value:
            return value
        time.sleep(.04)
    raise AssertionError('Own startup window did not reach the requested state')


def capture(hwnd, path):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    dc = win32gui.GetWindowDC(hwnd)
    source = win32ui.CreateDCFromHandle(dc)
    memory = source.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(source, right-left, bottom-top)
    memory.SelectObject(bitmap)
    try:
        import ctypes
        assert ctypes.windll.user32.PrintWindow(hwnd, memory.GetSafeHdc(), 2)
        picture = Image.frombuffer('RGB', (right-left, bottom-top), bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
        picture.save(path)
        assert max(picture.getextrema()[0]) > 100
        return picture
    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        memory.DeleteDC()
        source.DeleteDC()
        win32gui.ReleaseDC(hwnd, dc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', type=Path)
    args = parser.parse_args()
    report = Path('reports/rc104/splash-native')
    report.mkdir(parents=True, exist_ok=True)
    command = [str(args.exe)] if args.exe else [sys.executable, '-m', 'app']
    child = subprocess.Popen(command+['--startup-splash'], stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding='utf-8',
        creationflags=subprocess.CREATE_NO_WINDOW)
    control = StartupSplash(child)
    try:
        hwnd = until(lambda: next((h for h,t in windows(child) if 'Đang khởi động' in t), None))
        time.sleep(.15)
        one = capture(hwnd, report/'preparing.png')
        # The caller has no Qt loop and is deliberately blocked; child motion continues.
        time.sleep(.38)
        two = capture(hwnd, report/'animation.png')
        assert ImageChops.difference(one, two).getbbox(), 'Startup animation stopped with its caller'
        control.stage('library')
        until(lambda: 'Đang mở thư viện' in win32gui.GetWindowText(hwnd))
        control.stage('interface')
        until(lambda: 'Đang tải giao diện' in win32gui.GetWindowText(hwnd))
        time.sleep(.1)
        capture(hwnd, report/'interface.png')
        control.finish()
        assert child.wait(timeout=5) == 0
    finally:
        control.close()
        child.wait(timeout=7)
        errors = child.stderr.read()
        assert not errors.strip(), errors

    with tempfile.TemporaryDirectory(prefix='bcl-startup-', ignore_cleanup_errors=True) as folder:
        environment = dict(os.environ, BILICLASS_DATA=folder, BILICLASS_EXPERIMENTAL_TEACHING='0')
        desktop = subprocess.Popen(command+['--page', 'library'], env=environment,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            main_window = until(lambda: next((h for h,t in windows(desktop) if 'Trợ lý dạy học song ngữ' in t), None), timeout=35)
            until(lambda: not any('Đang khởi động' in t or 'Đang tải giao diện' in t or 'Đã sẵn sàng' in t for _,t in windows(desktop)), timeout=8)
            time.sleep(.2)
            win32gui.SendMessageTimeout(main_window, 0, 0, 0, 2, 500)
        finally:
            own_main = [h for h,t in windows(desktop) if 'Trợ lý dạy học song ngữ' in t]
            for hwnd in own_main:
                win32gui.PostMessage(hwnd, 0x10, 0, 0)
            assert desktop.wait(timeout=15) == 0
    result = {'status':'passed','scope':'own disposable profile/processes; no teacher data',
              'checks':['artwork and live phases render','animation continues while caller is blocked',
                        'ready/EOF closes dedicated child','normal desktop closes splash after first frame']}
    (report/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
