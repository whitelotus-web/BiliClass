"""Real Qt + Office: ready/F5, immutable binding, silent native audio, explicit switch."""

import json
import logging
import os
import shutil
import sys
import tempfile
from multiprocessing import freeze_support
from pathlib import Path

import win32con
import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QCoreApplication, QEvent, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import click, control, pump, until
from test_teaching_session import prepared_lesson

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    out = Path('reports/rc90/teaching')
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-teaching-', ignore_cleanup_errors=True) as folder:
        folder = Path(folder)
        lesson, preview, directory, original = prepared_lesson(folder)
        original_bytes = original.read_bytes()
        os.environ['BILICLASS_DATA'] = str(directory)
        library = Library(directory)
        other = library.create('Another lesson', 'Tin học', 'THPT', '10', [('Slide 1', 'Máy tính.')])
        other = library.edit_segment(other['id'], other['segments'][0]['id'], 'Máy tính.', 'A computer.')
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(RESOURCE_ROOT / 'qml/Main.qml')
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        def c(name):
            return control(window, name)
        companion = c('companionWindow')
        def cc(name):
            item = companion.findChild(QObject, name)
            assert item, name
            return item
        def tap(name):
            item = cc(name)
            # Invoke the control signal; the actual Office worker runs normally.
            item.clicked.emit()
            pump(100)
        try:
            # The same destination used by both conversion completion callbacks.
            window.setProperty('page', 'chatgpt')
            bridge._show_lesson(lesson, preview, destination='voice', auto_repair=False)
            until(lambda: not bridge.previewBusy and not bridge.busy)
            assert window.property('page') == 'voice'
            assert not c('voiceSourceArea').isVisible()
            assert not c('voiceDownloadWithoutNarration').isVisible(), 'Ready narration has a single main download/teach area'
            assert c('voiceDownloadWithoutNarrationMenu') is not None
            assert c('continueAfterNarrationButton').property('text') == 'Mở PowerPoint'
            assert window.findChild(QObject, 'navigationteach') is None
            for size in [(1080, 700), (1366, 850)]:
                window.resize(*size)
                pump(100)
                assert window.grabWindow().save(str(out / f'voice-{size[0]}.png'))
            # Ready voice opens a managed PowerPoint copy directly. No automatic approval/playback.
            before_revision = library.get(lesson['id'])['revision']
            window.setProperty('page', 'library')
            until(lambda: bridge._catalog.worker is None)
            pump(150)
            button = c('lessonOpen_' + lesson['id'])
            assert button.property('text') == 'Mở PowerPoint'
            click(window, button)
            until(lambda: bool(bridge.powerpointState.get('opened')), timeout=50)
            assert window.property('page') == 'library', 'Opening PowerPoint must not navigate to voice settings'
            assert not c('wholeLessonReview').property('visible')
            assert not bridge.powerpointState.get('active')
            assert library.get(lesson['id'])['revision'] == before_revision
            assert bridge.teachingSession.state['lesson_id'] == lesson['id']
            independent = folder / 'Downloaded with voice.pptx'
            shutil.copyfile(bridge.teachingSession.bound['path'], independent)
            assert companion.isVisible() and cc('companionStartShow').isVisible()
            assert companion.grabWindow().save(str(out / 'mascot-ready.png'))
            tap('companionStartShow')
            until(lambda: bridge.powerpointState.get('active'), timeout=50)
            assert bridge.teachingSession.audio == {'vi': True, 'en': True, 'both': True}
            assert bridge.powerpointState.get('hwnd'), 'Mascot must resolve this slideshow window when Office omits HWND'
            assert cc('companionReadingOptions').isVisible()
            assert companion.findChild(QObject, 'companionStopSpeech') is None
            assert companion.findChild(QObject, 'companionPauseEnglish') is None
            assert cc('companionReadEnglish').isVisible() and cc('companionReadVietnamese').isVisible()
            # Existing slide speakers and Mascot use PowerPoint's same native player.
            tap('companionReadEnglish')
            until(lambda: bridge.teachingSession.native_state == 'reading', timeout=10)
            assert cc('mascotCompanion').property('expression') == 'speaking', 'Native media updates the mascot state'
            assert bridge.english_reader.worker is None
            assert not bridge.english_reader.queue
            assert cc('companionReadEnglish').property('iconName') == 'pause'
            tap('companionReadEnglish')
            until(lambda: bridge.teachingSession.native_state == 'paused')
            assert cc('companionReadEnglish').property('iconName') == 'speaker-en'
            tap('companionReadEnglish')
            until(lambda: bridge.teachingSession.native_state == 'reading')
            tap('companionReadVietnamese')
            tap('companionReadEnglish')
            until(lambda: bridge.teachingSession.native_state == 'reading' and bridge.teachingSession.language == 'en')
            assert not bridge.english_reader.queue, 'Mouse controls must share native playback, not create a second voice queue'
            bridge.teachingSession.stop()
            pump(300)
            stale = {'language': 'en', 'slide_id': bridge.powerpointState['slide_id'],
                     'token': bridge.teachingSession.token}
            bridge.powerpoint_worker.navigate('goto', 3)
            bridge.powerpoint_worker.navigate('play_media', stale)
            until(lambda: bridge.powerpointState.get('slide') == 3)
            pump(350)
            assert bridge.teachingSession.native_state == 'stopped', 'Late slide 1 playback must not start on slide 3'
            bridge.powerpoint_worker.navigate('goto', 1)
            until(lambda: bridge.powerpointState.get('slide') == 1)
            tap('companionNext')
            until(lambda: bridge.powerpointState.get('slide') == 2)
            assert not cc('companionReadEnglish').isVisible() and not cc('companionReadVietnamese').isVisible()
            tap('companionNext')
            until(lambda: bridge.powerpointState.get('slide') == 3)
            assert cc('companionReadVietnamese').isVisible() and not cc('companionReadEnglish').isVisible()
            assert not cc('companionReadBoth').isVisible()
            bridge.openLesson(other['id'])
            until(lambda: not bridge.busy and bridge.lesson.get('id') == other['id'])
            assert bridge.teachingSession.state['lesson_id'] == lesson['id']
            assert bridge.powerpointState['active'] and bridge.powerpointState['slide'] == 3
            assert lesson['title'] in cc('companionBoundLesson').property('text')
            assert companion.grabWindow().save(str(out / 'mascot-browse-other.png'))
            window.showMinimized()
            pump(120)
            assert companion.isVisible() and bridge.powerpointState['active']
            assert win32gui.IsWindowVisible(int(companion.winId())) and not win32gui.IsIconic(int(companion.winId()))
            assert win32gui.GetWindowLong(int(companion.winId()), win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST
            tap('companionPrevious')
            until(lambda: bridge.powerpointState['slide'] == 2)
            tap('companionEndShow')
            until(lambda: not bridge.powerpointState.get('active') and bridge.powerpointState.get('opened'))
            assert bridge.teachingSession.state['lesson_id'] == lesson['id']
            # Floating Mascot and library share one direct open/bind route.
            tap('companionChooseLesson')
            assert cc('companionLibraryPicker').isVisible() and cc('companionSelectFile').isVisible()
            index = next(i for i, row in enumerate(bridge.lessons) if row['id'] == other['id'])
            cc('companionLibraryPicker').setProperty('currentIndex', index)
            tap('companionSelectLibrary')
            until(lambda: bridge.teachingSession.state.get('lesson_id') == other['id'] and bridge.powerpointState.get('opened'), timeout=50)
            assert not c('wholeLessonReview').property('visible')
            assert not bridge.powerpointState.get('active')
            tap('companionStartShow')
            until(lambda: bridge.powerpointState.get('active'))
            assert bridge.teachingSession.audio == {'vi': False, 'en': False, 'both': False}
            bridge.openTeachingPresentation(independent.as_uri())
            until(lambda: not bridge.busy and bridge.teachingSession.state.get('lesson_id') not in ('', other['id'])
                  and bridge.powerpointState.get('opened'), timeout=50)
            assert not bridge.error, bridge.message
            tap('companionStartShow')
            until(lambda: bridge.powerpointState.get('active'))
            assert bridge.teachingSession.audio == {'vi': True, 'en': True, 'both': True}
            tap('companionReadVietnamese')
            until(lambda: bridge.teachingSession.native_state == 'reading')
            bridge.teachingSession.stop()
            assert original.read_bytes() == original_bytes
            # Each teacher-facing Open entry uses the same direct binding path.
            # Keep a different managed presentation open to exercise replacement.
            from app.voice_import import prepare_library_lesson

            window.showNormal()
            converted = prepare_library_lesson(directory, other['id'])
            bridge._browser_state.update(phase='completed', lessonId=other['id'], running=False)
            bridge._show_lesson(*converted, destination='chatgpt', auto_repair=False, load_preview=False)
            pump(150)
            assert c('teachCompletedConversion').property('text') == 'Mở PowerPoint'
            click(window, c('teachCompletedConversion'))
            until(lambda: not bridge.busy and bridge.teachingSession.state.get('lesson_id') == other['id']
                  and bridge.powerpointState.get('opened'), timeout=50)
            assert window.property('page') == 'chatgpt' and not c('wholeLessonReview').property('visible')
            assert not bridge.powerpointState.get('active')
            print('Converted result opened and bound', flush=True)
            # Before voice creation, opening is still available and never synthesizes.
            window.setProperty('page', 'voice')
            pump(150)
            token = bridge.teachingSession.token
            click(window, c('voiceTeachWithoutNarration'))
            print('Before-voice open requested: ' + json.dumps({'busy': bridge.busy, 'message': bridge.message,
                  'token': bridge.teachingSession.token, 'previous_token': token}), flush=True)
            until(lambda: not bridge.busy and bridge.teachingSession.token != token
                  and bridge.powerpointState.get('opened') and not bridge.powerpointState.get('starting')
                  and not bridge._pending_teaching, timeout=50)
            assert window.property('page') == 'voice' and bridge.teachingSession.state['lesson_id'] == other['id']
            assert not bridge.narrationBusy and not c('wholeLessonReview').property('visible')
            # After voice creation, the selected ready variant replaces the old binding.
            bridge._show_lesson(library.get(lesson['id']), preview, destination='voice', auto_repair=False, load_preview=False)
            pump(150)
            assert c('continueAfterNarrationButton').isVisible()
            click(window, c('continueAfterNarrationButton'))
            until(lambda: not bridge.busy and bridge.teachingSession.state.get('lesson_id') == lesson['id']
                  and bridge.powerpointState.get('opened'), timeout=50)
            assert window.property('page') == 'voice' and not bridge.powerpointState.get('active')
            assert not c('wholeLessonReview').property('visible')
            assert not any(segment['approved'] for segment in library.get(lesson['id'])['segments'])
            bridge.stopPowerPoint()
            until(lambda: bridge.powerpoint_worker is None)
            assert not bridge.teachingSession.state['bound']
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings,
                      'checks': ['conversion destination opens configured voice page', 'no new sidebar tab',
                                 'no-voice download retained', 'ready and explicit F5', 'native silent embedded audio',
                                 'per-slide language buttons', 'browsing does not rebind', 'minimized app keeps Mascot',
                                 'floating library and file choices', 'direct switch without approval popup',
                                 'no-voice teaching', 'external PPTX with embedded voices', 'native pause/resume',
                                 'delayed playback rejected after native slide change',
                                 'direct Open and Mascot binding after conversion/before voice/after voice/in library',
                                 'source unchanged'],
                      'scope': 'Current Windows/Office, silent WAV fixtures; no physical projector or second monitor certification'}
            (out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        except BaseException:
            print('Failure state: ' + json.dumps({'busy': bridge.busy, 'error': bridge.error, 'message': bridge.message,
                  'native': bridge.powerpointState, 'bound': bridge.teachingSession.state.get('lesson_id'),
                  'pending': bool(bridge._pending_teaching), 'page': window.property('page')}), flush=True)
            window.grabWindow().save(str(out / 'failure.png'))
            raise
        finally:
            if bridge.powerpoint_worker:
                bridge.stopPowerPoint()
                until(lambda: bridge.powerpoint_worker is None, timeout=15)
            window.hide()
            companion.hide()
            for worker in (bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog, bridge.browserAI,
                           bridge.english_reader, bridge.narration_preparation, bridge.classroom, bridge.voice_controls):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
            logging.shutdown()


if __name__ == '__main__':
    freeze_support()
    main()
