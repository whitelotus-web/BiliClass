"""Qt last-choice defaults and language-specific samples; preserve old recordings."""

import hashlib
import json
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app import speech
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from app.voice_preview import EN_SAMPLE_TEXT, VI_SAMPLE_TEXT
from scripts.qt_result_preview_mascot_smoke import control, pump, until

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tests'))
from test_teaching_session import prepared_lesson


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    reports = Path('reports/rc100/voice-preferences')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-voice-defaults-', ignore_cleanup_errors=True) as folder:
        old_lesson, old_preview, directory, source = prepared_lesson(Path(folder))
        source_before = source.read_bytes()
        audio_before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (directory/'audio').glob('*.wav')}
        for phase in ('first', 'reopened'):
            library = Library(directory)
            fresh = library.create('Bài mới '+phase, 'Vật lý', 'THPT', '10', [('Mở đầu', 'Nội dung mới.')])
            fresh['segments'][0]['en'] = 'New lesson content.'
            library._write(fresh)
            bridge = Bridge(library)
            engine = QQmlApplicationEngine()
            warnings, calls = [], []
            engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
            engine.rootContext().setContextProperty('bridge', bridge)
            engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
            assert engine.rootObjects(), warnings
            root = engine.rootObjects()[0]

            def c(name):
                return control(root, name)

            try:
                settings = c('settingsPage')
                if phase == 'first':
                    root.setProperty('page', 'settings')
                    settings.setProperty('activeTab', 2)
                    c('selectMultilingualVoice6').clicked.emit()
                    c('saveMultilingualVoice').clicked.emit()
                    until(lambda: bridge.voice_controls.save_worker is None)
                    assert bridge.voiceSettings['voice'] == 'pair:truc-ly'
                else:
                    assert bridge.voiceSettings['voice'] == 'pair:north-male' and bridge.voiceSettings['rate'] == 2
                bridge._show_lesson(fresh, destination='voice', auto_repair=False, load_preview=False)
                pump(120)
                assert root.property('narrationVoice') == bridge.voiceSettings['voice']
                assert root.property('narrationRate') == bridge.voiceSettings['rate']
                bridge.voice_controls.preview = lambda *args: calls.append(args)
                for mode, name in (('en', 'narrationEnglish'), ('vi', 'narrationVietnamese'), ('both', 'narrationBoth')):
                    c(name).clicked.emit()
                    c('previewLessonNarrationVoice').clicked.emit()
                    assert len(calls) > 0
                    expected_voice = root.property('narrationVoice') if mode == 'both' else speech.voice_for(root.property('narrationVoice'), mode)
                    expected_text = VI_SAMPLE_TEXT+'\n'+EN_SAMPLE_TEXT if mode == 'both' else EN_SAMPLE_TEXT if mode == 'en' else VI_SAMPLE_TEXT
                    assert calls[-1] == (expected_text, expected_voice, root.property('narrationRate'))
                if phase == 'first':
                    choice = c('lessonNarrationVoiceChoice')
                    index = next(i for i, row in enumerate(bridge.multilingualVoices) if row['id'] == 'pair:north-male')
                    choice.setProperty('currentIndex', index)
                    choice.activated.emit(index)
                    speed = c('lessonNarrationRateChoice')
                    speed.setProperty('currentIndex', 5)
                    speed.activated.emit(5)
                    until(lambda: bridge.voice_controls.save_worker is None)
                    assert library.setting('voice_options', {}) == {'voice': 'pair:north-male', 'rate': 2}
                    assert settings.property('draftVoice') == 'pair:north-male' and settings.property('draftRate') == 2
                    root.setProperty('page', 'home')
                    bridge._show_lesson(fresh, destination='voice', auto_repair=False, load_preview=False)
                    assert root.property('narrationVoice') == 'pair:north-male' and root.property('narrationRate') == 2
                bridge._show_lesson(old_lesson, old_preview, destination='voice', auto_repair=False, load_preview=False)
                until(lambda: bridge.lessonNarration.get('ready'))
                assert bridge.lessonNarration['voice'] == old_lesson['narration']['voice']
                assert library.get(old_lesson['id'])['narration'] == old_lesson['narration']
                assert not warnings, warnings
            finally:
                for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                               bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                               bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                    worker.shutdown()
                c('companionWindow').setProperty('disposing', True)
                c('companionWindow').hide()
                root.hide()
                engine.deleteLater()
                QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
                app.processEvents()
                library.close()
        assert source.read_bytes() == source_before
        assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (directory/'audio').glob('*.wav')} == audio_before
        result = dict(status='passed', checks=['Saved Settings pair used for fresh lessons',
                      'Last deliberate creation pair/speed persist across navigation and restart; Settings synchronize',
                      'EN/VI/both previews use matching long Settings text and exact language voice/rate',
                      'Old narration product, WAVs and source remain unchanged'], qml_warnings=[])
        (reports/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
