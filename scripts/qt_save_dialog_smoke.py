"""Read the actual native Windows filename field, using disposable destinations."""

import json
import os
import tempfile
import time
from pathlib import Path

import win32gui
import win32process
from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.download_names import suggestion
from app.paths import RESOURCE_ROOT


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    engine = QQmlApplicationEngine()
    warnings = []
    engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
    engine.loadData(b'''import QtQuick
import QtQuick.Controls
ApplicationWindow {
    visible: true; width: 520; height: 220
    SuggestedSaveDialog { objectName: "save"; title: "BiliClass filename regression";
        defaultSuffix: "pptx"; nameFilters: ["PowerPoint (*.pptx)"] }
}''', QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/SaveDialogSmoke.qml')))
    assert engine.rootObjects(), warnings
    window = engine.rootObjects()[0]
    dialog = window.findChild(QObject, 'save')
    checked = []
    with tempfile.TemporaryDirectory(prefix='bcl-save-name-') as folder:
        cases = [('Bài 1. Hệ điều hành', 'Song ngữ Việt–Anh'),
                 ('Bài 2. Mạng máy tính', 'Có giọng Anh · Mai Anh · 100%')]
        pending = {'deadline': 0, 'target': None, 'error': ''}

        def open_next():
            if len(checked) == len(cases):
                app.quit()
                return
            title, suffix = cases[len(checked)]
            target = suggestion(folder, title, suffix, 'pptx')
            pending.update(target=target, deadline=time.monotonic() + 10)
            dialog.setProperty('currentFolder', QUrl.fromLocalFile(folder))
            dialog.setProperty('suggestedFile', QUrl.fromLocalFile(str(target)))
            QMetaObject.invokeMethod(dialog, 'openSuggested')

        def inspect():
            if pending['target'] is None:
                return
            found = []
            def inspect_window(handle, _):
                if win32process.GetWindowThreadProcessId(handle)[1] != os.getpid():
                    return
                if win32gui.GetWindowText(handle) != 'BiliClass filename regression':
                    return
                def child(control, _):
                    if win32gui.GetClassName(control) == 'Edit':
                        value = win32gui.GetWindowText(control)
                        if value in (pending['target'].name, pending['target'].stem):
                            found.append(value)
                win32gui.EnumChildWindows(handle, child, None)
            win32gui.EnumWindows(inspect_window, None)
            if found:
                checked.append(found[0])
                pending['target'] = None
                dialog.setProperty('visible', False)
                QTimer.singleShot(300, open_next)
            elif time.monotonic() > pending['deadline']:
                pending['error'] = 'Native filename blank/stale: ' + pending['target'].name
                app.exit(1)

        timer = QTimer()
        timer.timeout.connect(inspect)
        timer.start(100)
        QTimer.singleShot(300, open_next)
        app.exec()
        timer.stop()
        dialog.setProperty('visible', False)
        assert not pending['error'], pending['error']
        assert len(checked) == len(cases), checked
        assert not warnings, warnings
        out = Path('reports/rc73/save-dialog.json')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({'status': 'passed', 'native_filename_fields': checked,
                                   'qml_warnings': warnings}, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Native filename fields passed: bilingual and voice; reopen uses the new title.', flush=True)
    window.hide()
    engine.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    app.processEvents()


if __name__ == '__main__':
    main()
