"""Disposable Qt: six pairs, old recordings, three products, two playback buttons."""

import json
import os
import sys
import tempfile
import time
import wave
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app import speech
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.presentation_audio import slide_audio
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump, until

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tests'))
from test_teaching_session import prepared_lesson


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = Path(os.environ.get('BILICLASS_VOICE_PAIRS_REPORT', 'reports/rc94/voice-pairs-ui'))
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-pairs-', ignore_cleanup_errors=True) as folder:
        lesson, preview, directory, original = prepared_lesson(Path(folder))
        source = original.read_bytes()
        library = Library(directory)
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings, played, created = [], [], []
        engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        companion = control(root, 'companionWindow')
        old_render, old_secondary = speech.synthesize_background, speech.synthesize_secondary
        def render(text, voice, rate, directory, cancel):
            assert voice in {'kokoro-us:am_michael', 'vieneu:Mai Anh'}
            created.append((voice, text))
            destination = Path(directory)/(speech.audio_key(text, voice, rate)+'.wav')
            destination.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(destination), 'wb') as writer:
                writer.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
                writer.writeframes(bytes(4800))
            return {'path': str(destination), 'cached': False}
        try:
            bridge._play_audio = lambda path: played.append(path)
            root.setProperty('page', 'settings')
            settings = control(root, 'settingsPage')
            settings.setProperty('activeTab', 2)
            for index, pair in enumerate(speech.PAIRS):
                control(root, 'selectMultilingualVoice'+str(index)).clicked.emit()
                assert settings.property('draftVoice') == pair['id']
                control(root, 'previewMultilingualVoice').clicked.emit()
                until(lambda: len(played) == index+1)
                assert speech.valid_audio(played[-1])
                bridge.stopSpeech()
            for size in ((1080, 700), (1366, 850)):
                root.resize(*size)
                pump(120)
                assert root.grabWindow().save(str(report/f'settings-{size[0]}.png'))
            control(root, 'saveMultilingualVoice').clicked.emit()
            until(lambda: not bridge.voiceUiState['saving'])
            assert library.setting('voice_options', {})['voice'] == 'pair:south-male'
            vi_choice = control(root, 'settingsVietnameseVoice')
            vi_choice.setProperty('currentIndex', 0)
            vi_choice.activated.emit(0)
            custom = bridge.composeVoicePair('vieneu:Mai Anh', 'kokoro-us:am_michael')
            assert settings.property('draftVoice') == custom
            pump(80)
            assert control(root, 'settingsEnglishVoice').property('currentIndex') == 1
            for name in ('previewVietnameseVoice', 'previewEnglishVoice'):
                before = len(played)
                control(root, name).clicked.emit()
                until(lambda: len(played) == before + 1)
                assert speech.valid_audio(played[-1])
                bridge.stopSpeech()
            for size in ((1080, 700), (1366, 850)):
                root.resize(*size)
                pump(120)
                assert root.grabWindow().save(str(report/f'custom-settings-{size[0]}.png'))
            control(root, 'saveMultilingualVoice').clicked.emit()
            until(lambda: not bridge.voiceUiState['saving'])
            assert library.setting('voice_options', {})['voice'] == custom
            assert bridge.voiceSettings['voice'] == custom
            assert custom in {row['id'] for row in bridge.multilingualVoices}
            bridge._show_lesson(lesson, preview, destination='voice', auto_repair=False, load_preview=False)
            until(lambda: root.property('narrationComplete'))
            assert not control(root, 'createLessonNarrationButton').isEnabled()
            assert root.findChild(QObject, 'resultReadBoth') is None
            assert companion.findChild(QObject, 'companionReadBoth') is None
            control(root, 'toggleCompletedNarrationConfiguration').clicked.emit()
            pump(80)
            assert root.property('narrationOptionsPinned')
            speech.synthesize_background = speech.synthesize_secondary = render
            root.setProperty('narrationVoice', custom)
            for mode in ('en', 'vi', 'both'):
                root.setProperty('narrationMode', mode)
                pump(100)
                button = control(root, 'createLessonNarrationButton')
                assert button.isEnabled(), (mode, bridge.message)
                button.clicked.emit()
                until(lambda: not bridge.busy and not bridge.narrationBusy)
                until(lambda: bridge.lessonNarration.get('ready'))
                assert bridge._lesson['narration']['mode'] == mode
                assert bridge._lesson['narration']['playback'] == 'separate'
                pages = slide_audio(bridge._lesson, directory)
                assert set(pages[1]) == ({'en', 'vi'} if mode == 'both' else {mode})
            assert {voice for voice, _ in created} == {'kokoro-us:am_michael'}, 'Existing Vietnamese WAVs should be reused'
            assert original.read_bytes() == source
            # The teacher's old multilingual product is still present and ready.
            assert any(row.get('voice') == 'vieneu:Mai Anh' for row in bridge._lesson['narration_variants'].values())
            assert not warnings, warnings
            result = dict(status='passed', pairs=6, preview_playback=8, settings_saved=True,
                          custom_pair_saved=True, independent_language_previews=True,
                          old_voice_usable=True, creation_modes=3, combined_playback_removed=True,
                          new_pair_with_old_audio_can_create=True, source_preserved=True, warnings=warnings)
            (report/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            speech.synthesize_background, speech.synthesize_secondary = old_render, old_secondary
            bridge.teachingSession.clear()
            for task in (bridge.narration_preparation, bridge.english_reader, bridge.voice_controls,
                         bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                         bridge.narrationPreferences, bridge._companion_preferences):
                task.shutdown()
            bridge.classroom.shutdown()
            companion.setProperty('disposing', True)
            companion.hide()
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            library.close()
            app.processEvents()
            time.sleep(.05)


if __name__ == '__main__':
    main()
