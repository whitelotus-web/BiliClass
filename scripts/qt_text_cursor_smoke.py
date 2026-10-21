"""Exercise actual Windows text pointers and editing with a disposable library."""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import win32gui
from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt, QUrl
from PySide6.QtGui import QCursor, QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from qt_result_preview_mascot_smoke import click, control, pump


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT / 'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    report = Path(os.environ.get('BILICLASS_CURSOR_REPORT', 'reports/rc130/cursor'))
    report.mkdir(parents=True, exist_ok=True)
    baseline = '--baseline' in sys.argv
    previous = QCursor.pos()
    records = []
    with tempfile.TemporaryDirectory(prefix='bcl-text-cursor-', ignore_cleanup_errors=True) as temp:
        library = Library(Path(temp))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda items: warnings.extend(str(item) for item in items))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        window.setFlag(Qt.WindowStaysOnTopHint, True)
        window.resize(1366, 850)
        window.show()
        window.raise_()
        window.requestActivate()
        c = lambda name: control(window, name)
        ibeam = win32gui.LoadCursor(0, 32513)

        def hover(item, name, expected=True, x=None):
            point = item.mapToScene(QPointF(x if x is not None else 20, item.height()/2)).toPoint()
            assert 0 < point.x() < window.width() and 0 < point.y() < window.height(), (name, point)
            QCursor.setPos(window.mapToGlobal(point + type(point)(2, 0)))
            pump(20)
            QCursor.setPos(window.mapToGlobal(point))
            pump(100)
            native_point = win32gui.GetCursorPos()
            hit = win32gui.GetAncestor(win32gui.WindowFromPoint(native_point), 2)
            assert hit == int(window.winId()), (name, 'Test window was occluded', win32gui.GetWindowText(hit),
                                               native_point, win32gui.GetWindowRect(int(window.winId())),
                                               [point.x(), point.y()], win32gui.GetClassName(hit))
            actual = win32gui.GetCursorInfo()[1] == ibeam
            records.append(dict(name=name, ibeam=actual, expected=expected,
                                native_cursor=win32gui.GetCursorInfo()[1], expected_cursor=ibeam,
                                qt_cursor=window.cursor().shape().value))
            if not baseline:
                assert actual == expected, records[-1]

        try:
            for theme in (['dark'] if baseline else ['light', 'dark']):
                bridge.setApplicationTheme(theme)
                for page, name in [('library', 'librarySearch'), ('new', 'lessonTitle'),
                                   ('settings', 'settingsTeacher'), ('settings', 'settingsSchool')]:
                    window.setProperty('page', page)
                    c('settingsPage').setProperty('activeTab', 0)
                    pump(180)
                    item = c(name)
                    hover(item, theme + '/' + name + '/hover')
                    if baseline:
                        continue
                    click(window, item)
                    hover(item, theme + '/' + name + '/focus')
                    QTest.keyClick(window, Qt.Key_A, Qt.ControlModifier)
                    for character in 'cursor selection sample':
                        QTest.keyClick(window, Qt.Key(ord(character.upper())),
                                       Qt.ShiftModifier if character.isupper() else Qt.NoModifier)
                    assert item.property('text') == 'cursor selection sample', (name, item.property('text'), item.property('activeFocus'))
                    # Drag selection must remain in the text control, not a pointer overlay.
                    start = item.mapToScene(QPointF(item.property('leftPadding') + 2, item.height()/2)).toPoint()
                    end = start + type(start)(100, 0)
                    QTest.mousePress(window, Qt.LeftButton, Qt.NoModifier, start)
                    QTest.mouseMove(window, end, 80)
                    QTest.mouseRelease(window, Qt.LeftButton, Qt.NoModifier, end)
                    assert item.property('selectedText'), name
                    if name == 'librarySearch':
                        hover(c('libraryClearSearch'), theme + '/clear-button', False,
                              c('libraryClearSearch').width()/2)
                        click(window, c('libraryClearSearch'))
                        assert not item.property('text')
                    if name == 'settingsSchool':
                        item.setProperty('readOnly', True)
                        hover(item, theme + '/read-only-selectable')
                        item.setProperty('readOnly', False)
                        item.setEnabled(False)
                        hover(item, theme + '/disabled', False)
                        item.setEnabled(True)
                if not baseline:
                    c('settingsPage').setProperty('activeTab', 2)
                    pump(180)
                    for name in ('settingsVoiceSample', 'settingsEnglishVoiceSample'):
                        item = c(name)
                        click(window, item)
                        hover(item, theme + '/' + name)
                        QTest.keyClick(window, Qt.Key_A, Qt.ControlModifier)
                        QTest.keyClick(window, Qt.Key_X)
                        assert item.property('text') == 'x'
            if not baseline:
                window.setProperty('page', 'result')
                component = QQmlComponent(engine)
                component.setData(b'import QtQuick; import QtQuick.Controls; TextField { text: "abc"; x: 300; y: 160; width: 240; height: 44 }', QUrl())
                field = component.create()
                assert field is not None, component.errors()
                field.setParentItem(window.contentItem())
                pump(120)
                hover(field, 'result/back-layer-enabled')
                click(window, field)
                QTest.keyClick(window, Qt.Key_Backspace)
                assert field.property('text') == 'ab' and window.property('page') == 'result'
                field.setParentItem(None)
                field.deleteLater()
            assert not warnings, warnings
            result = dict(status='baseline' if baseline else 'passed', checks=records, warnings=warnings,
                          actual_native_cursor=True, device_pixel_ratio=window.devicePixelRatio())
            (report/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            window.hide()
            for worker in (bridge.inputDocuments, bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog,
                           bridge.browserAI, bridge.english_reader, bridge.narration_preparation, bridge.classroom,
                           bridge.voice_controls, bridge._companion_preferences):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
            QCursor.setPos(previous)


if __name__ == '__main__':
    main()
