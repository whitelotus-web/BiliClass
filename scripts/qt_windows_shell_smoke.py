"""Native caption/taskbar verification on a disposable Qt window and library."""

import ctypes
import json
import os
import tempfile
from ctypes import wintypes
from pathlib import Path

import win32con
import win32gui
import win32ui
from PIL import Image
from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from win32com.propsys import propsys, pscon

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from app.windows_identity import APP_ID, configure_window
from scripts.qt_result_preview_mascot_smoke import control, pump, until


def caption_capture(hwnd, path):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    dc = win32gui.GetWindowDC(hwnd)
    source = win32ui.CreateDCFromHandle(dc)
    memory = source.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(source, right-left, bottom-top)
    memory.SelectObject(bitmap)
    try:
        print_window = ctypes.windll.user32.PrintWindow
        print_window.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
        print_window.restype = wintypes.BOOL
        assert print_window(hwnd, memory.GetSafeHdc(), 2)
        Image.frombuffer('RGB', (right-left, bottom-top), bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1).save(path)
    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        memory.DeleteDC()
        source.DeleteDC()
        win32gui.ReleaseDC(hwnd, dc)


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    report = Path(os.environ.get('BILICLASS_SHELL_REPORT', 'reports/rc95/windows-shell'))
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-shell-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        library.set_setting('application_theme', os.environ.get('BILICLASS_SHELL_THEME', 'light'))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda entries: warnings.extend(map(str, entries)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')
        hwnd = int(root.winId())
        try:
            configure_window(root)
            root.showNormal()
            pump(200)
            store = propsys.SHGetPropertyStoreForWindow(hwnd, propsys.IID_IPropertyStore)
            assert store.GetValue(pscon.PKEY_AppUserModel_ID).GetValue() == APP_ID
            assert store.GetValue(pscon.PKEY_AppUserModel_RelaunchDisplayNameResource).GetValue() == 'BiliClass'
            icon = store.GetValue(pscon.PKEY_AppUserModel_RelaunchIconResource).GetValue()
            assert Path(icon.rsplit(',', 1)[0]).is_file()
            assert win32gui.SendMessage(hwnd, win32con.WM_GETICON, 0, 0)
            assert win32gui.SendMessage(hwnd, win32con.WM_GETICON, 1, 0)
            caption = control(root, 'applicationCaptionText')
            assert caption.property('text') == root.title()
            assert caption.property('color').name() == ('#e6edf7' if bridge.applicationTheme == 'dark' else '#112650')
            assert not root.flags() & Qt.WindowTitleHint, 'Avoid a second, platform-painted caption over QML text'
            for width, height in [(1080, 700), (1366, 850), (1680, 960)]:
                root.resize(width, height)
                pump(200)
                bar = control(root, 'applicationTitleBar')
                badges = control(root, 'applicationTitleBadges')
                assert 24 <= bar.height()*root.devicePixelRatio() <= 60
                assert bar.height() >= badges.height()
                assert badges.mapToScene(QPointF()).y() >= 0
                assert 250 < badges.x() < 450 and badges.x() + badges.width() <= width - 155
                assert badges.height() == 20 and badges.property('spacing') == 8
                assert control(root, 'mainPageArea').mapToScene(QPointF()).y() == bar.height()
                assert root.grabWindow().save(str(report / f'client-{width}.png'))
                caption_capture(hwnd, report / f'caption-{width}.png')
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MAXIMIZE, 0)
            until(lambda: root.visibility() == root.Visibility.Maximized)
            pump(120)
            caption_capture(hwnd, report / 'caption-maximized.png')
            assert root.frameGeometry().height() <= root.screen().availableGeometry().height() + 16
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
            until(lambda: root.visibility() == root.Visibility.Minimized)
            root.showNormal()
            pump(100)
            assert not root.flags() & Qt.FramelessWindowHint
            assert 'Trợ lý dạy học song ngữ' in win32gui.GetWindowText(hwnd)
            assert not warnings, warnings
            result = dict(status='passed', system_window_controls=True, single_qml_caption=True,
                          theme=bridge.applicationTheme, colored_badges_sizes=3,
                          minimize_maximize_restore=True, taskbar_window_properties=True,
                          valid_small_large_icons=True, qml_warnings=warnings)
            (report / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result))
        finally:
            companion.setProperty('disposing', True)
            root.close()
            for worker in (bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog, bridge.browserAI,
                           bridge.english_reader, bridge.narration_preparation, bridge.classroom, bridge.voice_controls,
                           bridge.narrationPreferences, bridge._companion_preferences):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            library.close()
    return 0


if __name__ == '__main__':
    if os.name != 'nt':
        raise SystemExit('Windows only')
    raise SystemExit(main())
