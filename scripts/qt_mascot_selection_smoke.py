"""Mascot selection survives catalog reorder/removal; native file dialog opens and cancels."""
import argparse
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report-dir', type=Path, default=Path('reports/mascot-selection'))
    report = parser.parse_args().report_dir
    report.mkdir(parents=True, exist_ok=True)
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    with tempfile.TemporaryDirectory(prefix='bcl-picker-', ignore_cleanup_errors=True) as temporary:
        library = Library(Path(temporary))
        first = library.create('A — Bài cần mở', 'Toán', 'THPT', '11', [('Slide 1', 'Điểm A.')])
        library.create('B — Bài khác', 'Toán', 'THPT', '11', [('Slide 1', 'Điểm B.')])
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')
        try:
            until(lambda: len(bridge.lessons) == 2 and bridge._catalog.worker is None)
            bridge.setLessonOrder('title_asc')
            pump(80)
            picker = control(root, 'companionLibraryPicker')
            target = next(i for i, row in enumerate(bridge.lessons) if row['id'] == first['id'])
            picker.setProperty('currentIndex', target)
            QMetaObject.invokeMethod(picker, 'activated', Qt.DirectConnection, Q_ARG(int, target))
            library.update_metadata(first['id'], 'Z — Bài đã đổi tên', 'Toán', 'THPT', '11')
            bridge._catalog.refresh(force=True)
            until(lambda: bridge._catalog.worker is None)
            pump(100)
            opened = []
            with patch.object(bridge, '_open_teaching_library', side_effect=lambda identity, **_: opened.append(identity)):
                control(root, 'companionSelectLibrary').clicked.emit()
            assert opened == [first['id']]
            assert picker.property('currentText') == 'Z — Bài đã đổi tên'
            library.trash_lesson(first['id'])
            bridge._catalog.refresh(force=True)
            until(lambda: bridge._catalog.worker is None)
            pump(80)
            assert picker.property('currentIndex') == -1
            assert not control(root, 'companionSelectLibrary').isEnabled()
            assert 'không còn' in picker.property('displayText')
            library.restore_lesson(first['id'])
            bridge._catalog.refresh(force=True)
            until(lambda: bridge._catalog.worker is None)
            pump(80)
            assert picker.property('currentValue') == first['id']
            # Use pointer events only in this owned Qt window, no global input.
            companion.setProperty('collapsed', False)
            companion.setProperty('choosingLesson', True)
            bridge.showCompanion(companion)
            pump(200)
            dialog = control(root, 'companionPresentationDialog')
            click(companion, control(root, 'companionSelectFile'))
            until(lambda: dialog.property('visible'))
            dialog.setProperty('visible', False)
            pump(80)
            assert not bridge.busy and not bridge.powerpoint_worker, 'Cancel never starts an open job'
            assert not warnings, warnings
            (report/'result.json').write_text(json.dumps(dict(status='passed',
                selection_survives_reorder=True, missing_selection_disabled=True, restored_identity_retained=True,
                native_file_dialog_open_cancel=True, no_global_input=True, qml_warnings=[])), encoding='utf-8')
            print('Mascot stable lesson selection and native file open/cancel passed.', flush=True)
        finally:
            for service in (bridge._catalog, bridge._library_preferences, bridge.browserAI, bridge.googleSettings,
                            bridge.slidePreview, bridge.libraryThumbnails, bridge.narrationPreferences,
                            bridge.narration_preparation, bridge.english_reader, bridge.voice_controls,
                            bridge._companion_preferences, bridge.classroom):
                service.shutdown()
            companion.setProperty('disposing', True)
            companion.hide()
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
