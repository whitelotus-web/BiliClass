"""Completed narration, automatic slide preview, and compact actions in real Qt.

Uses a disposable library, real Office preview and cached fixture WAVs. Does not
send global input or open/close any teacher presentation.
"""
import json
import sys
import tempfile
import wave
from pathlib import Path
from unittest.mock import patch

from pptx import Presentation
from pptx.util import Inches
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPointF, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.branding import configure_application
from app.chatgpt_handoff import external_preview
from app.lesson_narration import make_plan, variant_id
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from app.voice_import import import_presentation
from scripts.qt_result_preview_mascot_smoke import control, pump, until


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT / 'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    reports = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/rc106/completed-voice')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-completed-voice-', ignore_cleanup_errors=True) as folder:
        folder = Path(folder)
        source = folder / 'Bài 4 – Độ dịch chuyển.pptx'
        presentation = Presentation()
        for n in (1, 2, 3):
            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(3)).text = (
                f'Bài 4: Độ dịch chuyển\nLesson 4: Displacement\nSlide {n}')
            slide.notes_slide.notes_text_frame.text = f'VI: Bài 4. Slide {n}.\nEN: Lesson 4. Slide {n}.'
        presentation.save(source)
        lesson, _ = import_presentation(folder / 'data', source)
        library = Library(folder / 'data')
        plan, _ = make_plan(lesson, 'both', {'voice': 'pair:truc-ly', 'rate': 0}, playback='both_controls')
        for keys in plan['keys'].values():
            for key in keys:
                target = library.directory / 'audio' / (key + '.wav')
                target.parent.mkdir(exist_ok=True)
                with wave.open(str(target), 'wb') as audio:
                    audio.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                    audio.writeframes(b'\1\0' * 2400)
        plan.update(lesson_id=lesson['id'], revision=lesson['revision'], complete=plan['total'], running=False)
        lesson = library.update_narration(lesson['id'], plan)
        lesson = library.select_narration_variant(lesson['id'], variant_id(plan))
        preview = external_preview(lesson, library.directory)
        bridge = Bridge(library)
        initial_powerpoint_state = dict(bridge.powerpointState)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]

        def c(name):
            return control(window, name)

        try:
            window.show()
            bridge._show_lesson(lesson, preview, destination='voice', auto_repair=False, load_preview=False)
            until(lambda: window.property('narrationComplete'), timeout=30)
            until(lambda: bool(bridge.quickResult.get('image')) and not bridge.previewBusy, timeout=90)
            assert window.property('voicePreviewExpanded')
            assert c('convertedSlideImage').property('source').toString()
            assert window.findChild(QObject, 'checkCompletedNarrationButton') is None
            assert 'Kiểm tra slide và giọng' not in (RESOURCE_ROOT / 'qml/NarrationReadyCard.qml').read_text(encoding='utf-8')
            for width, height in ((1080, 700), (1366, 850)):
                window.resize(width, height)
                pump(150)
                for name in ('resultPreviousSlide', 'resultSlideCounter', 'resultNextSlide',
                             'listenCreatedEnglish', 'listenCreatedVietnamese', 'stopCreatedNarration'):
                    item = c(name)
                    assert item.isVisible(), name
                    assert item.mapToScene(QPointF()).x() >= 0
                    assert item.mapToScene(QPointF(item.width(), 0)).x() <= width
                    assert abs(item.mapToScene(QPointF(0, item.height()/2)).y()
                               - c('resultSlideCounter').mapToScene(QPointF(0, c('resultSlideCounter').height()/2)).y()) < 2
                viewport = c('resultScroll').property('contentItem')
                viewport.setProperty('contentY', max(0, viewport.property('contentHeight') - viewport.height()))
                pump(180)
                assert window.grabWindow().save(str(reports / f'completed-{width}.png'))
            bridge._powerpoint_state = {**initial_powerpoint_state, 'active': True, 'starting': False}
            bridge.powerpointStateChanged.emit()
            with patch.object(bridge, 'stopSpeech') as stopped:
                bridge.previewConvertedSlide(2)
                until(lambda: not bridge.previewBusy, timeout=90)
                assert bridge.quickResult['slide'] == 2 and bridge.quickResult['image']
                stopped.assert_not_called()
            assert c('resultNextSlide').isEnabled()
            assert c('downloadAfterNarrationButton').isEnabled()
            assert not c('continueAfterNarrationButton').isEnabled()
            bridge._powerpoint_state = dict(initial_powerpoint_state)
            bridge.powerpointStateChanged.emit()
            c('toggleVoiceSlidePreview').clicked.emit()
            pump(100)
            assert not window.property('voicePreviewExpanded')
            window.setProperty('page', 'library')
            window.setProperty('page', 'voice')
            pump(150)
            assert window.property('voicePreviewExpanded'), 'Returning to a completed voice shows its preview'
            assert not warnings, warnings
            (reports / 'result.json').write_text(json.dumps({'status': 'passed', 'automatic_preview': True,
                'preview_while_powerpoint_active': True, 'sizes': [[1080, 700], [1366, 850]], 'qml_warnings': warnings}), encoding='utf-8')
            print('Completed narration Qt flow passed.', flush=True)
        finally:
            bridge._powerpoint_state = dict(initial_powerpoint_state)
            for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                           bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                           bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                worker.shutdown()
            c('companionWindow').setProperty('disposing', True)
            c('companionWindow').hide()
            window.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            pump(80)
            library.close()


if __name__ == '__main__':
    main()
