"""Delete/undo in disposable real Qt; never touches the teacher library or Office."""

import json
import sys
import tempfile
from pathlib import Path
from threading import Event
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app import library_actions
from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT/'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    report = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/library-undo')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-library-undo-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder)/'data')
        originals = [library.create(f'Bài thử {n}', 'Toán', 'THPT', '11', [('Slide 1', 'Nội dung.')]) for n in range(3)]
        ids = [row['id'] for row in originals]
        assets = {library.directory/'sources/fixture.pptx': b'original presentation',
                  library.directory/'audio/fixture.wav': b'original narration'}
        for path, data in assets.items():
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(data)
        bridge = Bridge(library)
        bridge.libraryThumbnails.request = lambda *_: None
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        release = Event()

        def c(name):
            return control(window, name)

        def settled(active, undo):
            until(lambda: not bridge.busy and len(bridge.lessons) == active and bridge.undoDeleteCount == undo)
            pump(100)

        try:
            window.resize(1366, 850)
            window.setProperty('page', 'library')
            window.show()
            settled(3, 0)
            assert not c('undoLibraryDeletion').isVisible()
            click(window, c('lessonDelete_'+ids[0]))
            click(window, c('cancelDeleteLessonButton'))
            settled(3, 0)
            click(window, c('lessonDelete_'+ids[0]))
            click(window, c('confirmDeleteLessonButton'))
            settled(2, 1)
            undo = c('undoLibraryDeletion')
            for theme in ('light', 'dark'):
                bridge.setApplicationTheme(theme)
                for width, height in ((1080, 700), (1366, 850)):
                    window.resize(width, height)
                    pump(120)
                    management = c('libraryManagementButton')
                    assert undo.isVisible() and undo.isEnabled()
                    assert undo.mapToScene(QPointF()).x() >= management.mapToScene(QPointF(management.width(), 0)).x() + 8
                    assert undo.mapToScene(QPointF(undo.width(), 0)).x() <= width - 15
                    assert abs(undo.mapToScene(QPointF(0, undo.height()/2)).y()
                               - management.mapToScene(QPointF(0, management.height()/2)).y()) <= 1
                    assert window.grabWindow().save(str(report/f'undo-{theme}-{width}.png'))
            first_receipt = dict(bridge._deleted_undo)
            assert bridge.trashLessons([ids[1], 'missing'])
            settled(2, 1)
            assert bridge.error and bridge._deleted_undo == first_receipt
            entered = Event()
            change = library_actions.change

            def held_change(*args, **kwargs):
                entered.set()
                assert release.wait(10)
                return change(*args, **kwargs)

            with patch('app.library_actions.change', side_effect=held_change):
                assert bridge.trashLessons([ids[1]])
                until(entered.is_set)
                assert not undo.isEnabled() and not bridge.undoDeletion()
                assert bridge._deleted_undo == first_receipt
                release.set()
                settled(1, 1)
            assert set(bridge._deleted_undo) == {ids[1]}, 'Only the latest successful batch is undoable'
            with patch('app.library_actions.change', side_effect=OSError('Fixture restore failure')):
                click(window, undo)
                settled(1, 1)
                assert bridge.error and undo.isEnabled(), 'A failed undo must remain retryable'
            undo.forceActiveFocus(Qt.OtherFocusReason)
            QTest.keyClick(window, Qt.Key_Space)
            settled(2, 0)
            assert library.get(ids[1]) == originals[1]
            assert library.get(ids[0], include_trash=True)['deleted_at'], 'Older deletion is untouched'
            bridge.restoreLessons([ids[0]])
            settled(3, 0)
            window.setProperty('selectedLessons', ids[:2])
            click(window, c('libraryDeleteSelected'))
            click(window, c('confirmBulkDeleteLessons'))
            settled(1, 2)
            click(window, undo)
            settled(3, 0)
            assert all(library.get(row['id']) == row for row in originals)

            # Details use the same confirmation and background deletion as a row.
            preview = dict(path=str(next(iter(assets))), lesson_id=ids[2], revision=originals[2]['revision'], total=1, slide=1)
            bridge._show_lesson(originals[2], preview, auto_repair=False, load_preview=False)
            until(lambda: window.property('page') == 'result')
            for width, height in ((1080, 700), (1366, 850)):
                window.resize(width, height)
                pump(120)
                delete, voice = c('resultDeleteLessonButton'), c('resultCreateNarrationButton')
                assert delete.isVisible() and delete.isEnabled()
                assert delete.mapToScene(QPointF()).x() > voice.mapToScene(QPointF(voice.width(), 0)).x()
                assert abs(delete.mapToScene(QPointF()).y() - voice.mapToScene(QPointF()).y()) <= 1
                assert window.grabWindow().save(str(report/f'details-delete-{width}.png'))
            click(window, delete)
            click(window, c('cancelDeleteLessonButton'))
            assert window.property('page') == 'result' and library.get(ids[2]) == originals[2]
            click(window, delete)
            click(window, c('confirmDeleteLessonButton'))
            settled(2, 1)
            assert window.property('page') == 'library' and not bridge.lesson
            click(window, undo)
            settled(3, 0)
            assert library.get(ids[2]) == originals[2]
            assert all(path.read_bytes() == data for path, data in assets.items())
            assert not warnings, warnings
            (report/'result.json').write_text(json.dumps(dict(status='passed', single_and_batch_undo=True,
                last_successful_batch_only=True, cancelled_or_failed_delete_keeps_undo=True,
                failed_undo_retryable=True, busy_guard_and_keyboard=True, detail_delete_returns_to_library=True,
                source_audio_and_metadata_preserved=True, qml_warnings=warnings)), encoding='utf-8')
            print('Library delete/undo Qt flow passed.', flush=True)
        finally:
            release.set()
            until(lambda: not bridge.busy)
            for service in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                            bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                            bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                service.shutdown()
            c('companionWindow').setProperty('disposing', True)
            c('companionWindow').hide()
            window.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            pump(80)
            library.close()


if __name__ == '__main__':
    main()
