"""Own Qt windows and disposable data: slow disk/SQLite must not block input."""

import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from threading import Event
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QThread, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app import google_settings, library_actions
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = Path(os.environ.get('BILICLASS_RESPONSIVENESS_REPORT', 'reports/rc102/responsiveness'))
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-responsive-', ignore_cleanup_errors=True) as folder:
        directory = Path(folder)
        library = Library(directory)
        identities = [library.create(f'Bài thử {n+1}', 'Toán', 'THPT', '11',
                                     [('Tiêu đề', 'Nội dung bài học.')])['id'] for n in range(24)]
        source, audio = directory/'sources'/'keep.pptx', directory/'audio'/'keep.wav'
        source.parent.mkdir(exist_ok=True)
        audio.parent.mkdir(exist_ok=True)
        source.write_bytes(b'preserve source')
        audio.write_bytes(b'preserve voice')
        bridge = Bridge(library)
        bridge.libraryThumbnails.request = lambda *_: None
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        root.resize(1366, 850)
        beats = []
        timer = QTimer()
        timer.setInterval(20)
        timer.timeout.connect(lambda: beats.append(time.monotonic()))

        def c(name):
            return control(root, name)

        def selected():
            value = root.property('selectedLessons')
            return value.toVariant() if hasattr(value, 'toVariant') else value

        def tracked(action, done):
            beats.clear()
            timer.start()
            start = time.monotonic()
            action()
            assert time.monotonic()-start < .5, 'Operation blocked before returning to Qt'
            until(done, timeout=20)
            pump(80)
            timer.stop()
            assert len(beats) >= 20, beats
            gap = max([beats[0]-start] + [b-a for a,b in zip(beats, beats[1:])])
            assert gap < .65, ('Qt heartbeat stalled', gap)
            return gap

        try:
            root.setProperty('page', 'library')
            until(lambda: len(bridge.lessons) == 24 and bridge.googleSettings.worker is None)
            pump(100)
            held = sqlite3.connect(directory/'library.db')
            held.execute('BEGIN IMMEDIATE')
            root.setProperty('selectedLessons', identities[:20])
            click(root, c('libraryDeleteSelected'))
            pump(40)

            def delete_under_lock():
                QTimer.singleShot(1200, held.commit)
                click(root, c('confirmBulkDeleteLessons'))
                assert bridge.busy and not bridge.jobCancellable
                assert set(selected()) == set(identities[:20]), 'Selection was cleared before commit'
                assert not c('applicationCancel').isVisible()
                assert not bridge.trashLessons([identities[20]]), 'Repeated click started another writer'
                bridge.cancelJob()
                assert not bridge.cancel_event.is_set(), 'An atomic write was marked canceled'
                c('librarySearch').setProperty('text', 'bài thử')
                bridge.setLibraryView('grid')
                bridge.setLessonOrder('title_asc')
                assert bridge.libraryView == 'grid' and bridge.lessonOrder == 'title_asc'
                root.resize(1080, 700)

            gaps = [tracked(delete_under_lock, lambda: not bridge.busy and len(bridge.lessons) == 4)]
            held.close()
            until(lambda: bridge._library_preferences.worker is None and not bridge._library_preferences.pending)
            assert library.setting('library_view', '') == 'grid' and library.setting('lesson_order', '') == 'title_asc'
            assert not selected() and len(bridge.trashedLessons) == 20
            change = library_actions.change

            def slow_change(*args):
                assert QThread.currentThread() != app.thread()
                time.sleep(.9)
                return change(*args)

            with patch.object(library_actions, 'change', slow_change):
                gaps.append(tracked(lambda: bridge.restoreLessons(identities[:20]),
                    lambda: not bridge.busy and len(bridge.lessons) == 24))
                root.setProperty('selectedLessons', identities[:2])
                gaps.append(tracked(lambda: bridge.trashLessons([identities[0], 'missing']), lambda: not bridge.busy))
                assert len(library.list_lessons()) == 24 and set(selected()) == set(identities[:2])
                gaps.append(tracked(lambda: bridge.trashLessons(identities[:20]),
                    lambda: not bridge.busy and len(bridge.trashedLessons) == 20))
                gaps.append(tracked(lambda: bridge.purgeLessons(identities[:20]),
                    lambda: not bridge.busy and len(bridge.trashedLessons) == 0))
            assert source.read_bytes() == b'preserve source' and audio.read_bytes() == b'preserve voice'

            until(lambda: bridge.googleSettings.worker is None)
            read = google_settings.read_state
            calls = []

            def slow_read(*args):
                assert QThread.currentThread() != app.thread()
                calls.append(1)
                time.sleep(.9)
                return read(*args)

            with patch.object(google_settings, 'read_state', slow_read):
                gaps.append(tracked(lambda: [bridge.googleSettings.refresh() for _ in range(10)],
                    lambda: bridge.googleSettings.worker is None))
                assert len(calls) == 2, 'Refresh requests were not coalesced'
            root.setProperty('page', 'settings')
            c('settingsPage').setProperty('activeTab', 6)
            root.resize(1366, 850)
            pump(100)
            until(lambda: bridge.googleSettings.worker is None)
            typed = 'Project A | AIza'+'a'*35
            c('googleApiKeys').setProperty('text', typed)
            mutate = google_settings.change

            def slow_save(*args):
                assert QThread.currentThread() != app.thread()
                time.sleep(.9)
                return mutate(*args)

            # A refresh begun before Save must never publish its stale result afterwards.
            old = dict(bridge.googleSettings.state)
            gate, started = Event(), Event()

            def stale_read(*args):
                started.set()
                assert gate.wait(10)
                return old

            with patch.object(google_settings, 'read_state', stale_read):
                bridge.googleSettings.refresh()
                until(started.is_set)
                with patch.object(google_settings, 'change', slow_save):
                    def save():
                        click(root, c('saveGoogleApiKeys'))
                        assert c('googleApiKeys').property('text') == typed
                        assert c('googleApiKeys').property('readOnly')
                    gaps.append(tracked(save, lambda: not bridge.busy))
                assert bridge.googleSettings.state['configured']
                assert not c('googleApiKeys').property('text')
                gate.set()
                until(lambda: bridge.googleSettings.worker is None)
                assert bridge.googleSettings.state['configured'], 'Old refresh overwrote a newer save'

            click(root, c('toggleGoogleKeyEntry'))
            c('googleApiKeys').setProperty('text', typed+'b')

            def failed_save(*args):
                time.sleep(.9)
                return {'state': None, 'error': 'Lỗi đọc lại thử nghiệm.'}

            with patch.object(google_settings, 'change', failed_save):
                gaps.append(tracked(lambda: click(root, c('saveGoogleApiKeys')), lambda: not bridge.busy))
            assert c('googleApiKeys').property('text') == typed+'b', 'Failed save erased the draft'
            assert all('key' not in row for row in bridge.googleSettings.state['keys'])
            assert not warnings, warnings
            result = dict(status='passed', max_ui_gap_seconds=round(max(gaps), 3), qml_warnings=[], checks=[
                'Bulk trash remains responsive while a separate SQLite writer holds the DB',
                'Restore/purge run on workers; duplicate requests and cancellation cannot corrupt atomic writes',
                'Failed batch preserves rows and selection; source/WAV preserved after permanent deletion',
                'Slow periodic key/model reads stay off Qt and coalesce repeated refresh requests',
                'Key save stays responsive; stale refresh ignored; failed save retains input; only masked metadata reaches QML'])
            (report/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            timer.stop()
            for service in (bridge.googleSettings, bridge._library_preferences, bridge._catalog, bridge.browserAI, bridge.slidePreview,
                            bridge.libraryThumbnails, bridge.narrationPreferences, bridge.narration_preparation,
                            bridge.english_reader, bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                service.shutdown()
            c('companionWindow').setProperty('disposing', True)
            c('companionWindow').hide()
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
