"""Disposable Qt check for source and frozen settings, with no model inference."""

import json
import tempfile
import time
import traceback
from pathlib import Path


def run(output):
    from PySide6.QtCore import (
        QCoreApplication,
        QEvent,
        QEventLoop,
        QMetaObject,
        QObject,
        QPointF,
        Qt,
        QTimer,
        QUrl,
    )
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuickControls2 import QQuickStyle

    from . import speech, voice_preview
    from .branding import configure_application
    from .library import Library
    from .paths import RESOURCE_ROOT
    from .ui import Bridge

    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    result = {'status': 'failed', 'scope': 'disposable Qt settings; bundled samples; no Google or TTS inference'}
    bridge = engine = window = library = None
    old_play, old_preview, old_engine = speech.play, voice_preview.preview, speech._vieneu_engine
    workspace = tempfile.TemporaryDirectory(prefix='bcl-voice-check-', ignore_cleanup_errors=True)
    beats, played = [], []
    timer = QTimer()

    def pump(ms=20):
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()

    def until(check, timeout=8):
        deadline = time.perf_counter() + timeout
        while not check():
            assert time.perf_counter() < deadline, 'Settings check timed out'
            pump(10)

    try:
        library = Library(workspace.name)
        bridge = Bridge(library)
        assert len(bridge.multilingualVoices) == 6, 'Missing offline voice pack'
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        window.resize(1080, 700)
        window.setProperty('page', 'settings')

        def control(name):
            found = window.findChild(QObject, name)
            if found is not None:
                return found
            pending = [window.contentItem()]
            while pending:
                item = pending.pop()
                if item.objectName() == name:
                    return item
                pending.extend(item.childItems())
            raise AssertionError(name)

        def click(name):
            item = control(name)
            assert item.property('enabled'), name
            assert QMetaObject.invokeMethod(item, 'clicked', Qt.DirectConnection), name

        settings = control('settingsPage')
        settings.setProperty('activeTab', 2)
        pump(150)

        def record_play(path):
            assert speech.valid_audio(path)
            played.append((time.perf_counter(), str(path)))
            if len(played) == 1:
                old_play(path)  # Exercise the installed Windows output once.

        def forbidden_engine(*_):
            raise AssertionError('A bundled settings sample attempted TTS inference')

        speech.play, speech._vieneu_engine = record_play, forbidden_engine
        timer.setInterval(20)
        timer.timeout.connect(lambda: beats.append(time.perf_counter()))
        timer.start()
        latencies = []
        for index in range(6):
            click('selectMultilingualVoice' + str(index))
            settings.setProperty('draftRate', 0)
            mark, count = time.perf_counter(), len(played)
            click('previewMultilingualVoice')
            assert not bridge.busy
            until(lambda: len(played) == count + 1 or bridge.voiceUiState['phase'] == 'error')
            assert len(played) == count + 1, bridge.voiceUiState
            latencies.append(time.perf_counter() - mark)
            bridge.stopSpeech()
        # A speed change must reuse the sample and keep the model unloaded.
        settings.setProperty('draftRate', 2)
        count = len(played)
        click('previewMultilingualVoice')
        until(lambda: len(played) == count + 1 or bridge.voiceUiState['phase'] == 'error')
        assert len(played) == count + 1, bridge.voiceUiState
        bridge.stopSpeech()

        def delayed(text, voice, rate, directory, *, cancel=None):
            if text == 'Câu riêng đang chuẩn bị.':
                cancel.wait(.8)
                return {'path': played[0][1]}
            return old_preview(text, voice, rate, directory, cancel=cancel)

        voice_preview.preview = delayed
        control('settingsVoiceSample').setProperty('text', 'Câu riêng đang chuẩn bị.')
        click('previewMultilingualVoice')
        assert bridge.voiceUiState['phase'] == 'preparing' and not bridge.busy
        mark = time.perf_counter()
        click('saveMultilingualVoice')
        until(lambda: not bridge.voiceUiState['saving'])
        saved_seconds = time.perf_counter() - mark
        assert not bridge.voiceUiState['saveError']
        assert library.setting('voice_options', {}) == {'voice': 'vieneu:Quang Sơn', 'rate': 2}
        assert 'Đã lưu' in control('voiceSaveStatus').property('text')
        count = len(played)
        click('stopVoicePreview')
        until(lambda: not bridge.voice_controls.preview_workers)
        assert len(played) == count, 'Cancelled preview played after Stop'
        assert window.grabWindow().save(str(output.with_name('voice-settings.png')))
        timer.stop()

        settings.setProperty('activeTab', 3)
        window.resize(1366, 900)
        pump(100)
        target = control('mascotThemeDescription')
        ancestor = target.parentItem()
        while ancestor is not None:
            if ancestor.metaObject().indexOfProperty('contentY') >= 0:
                offset = target.mapToItem(ancestor, QPointF(0, 0)).y()
                ancestor.setProperty('contentY', max(0, ancestor.property('contentY') + offset - ancestor.height() + 80))
            ancestor = ancestor.parentItem()
        pump(100)
        choices = bridge.conversionSubjects
        preview_lesson = library.create('Mascot preview fixture', 'Vật lý', 'THPT', '11', [('Thử phụ kiện', 'Fixture')])
        for removed in ('mascotSubject', 'mascotSubjectMode', 'mascotOtherSubject'):
            assert window.findChild(QObject, removed) is None
        themes = {}
        for subject in choices[:-1]:
            bridge._lesson = {**preview_lesson, 'subject': subject}
            bridge.changed.emit()
            settings.setProperty('selectedAccessorySubject', subject)
            pump(20)
            theme = control('mascotPreview').property('theme')
            theme = theme.toVariant() if hasattr(theme, 'toVariant') else theme
            assert theme['id'] != 'general', subject
            themes[subject] = theme['id']
        assert themes['Khoa học'] == themes['Khoa học tự nhiên'] == 'science'
        assert themes['Hóa học'] == 'chemistry'
        for subject in ('Vật lý', 'Hóa học', 'Tin học', 'Địa lí'):
            bridge._lesson = {**preview_lesson, 'subject': subject}
            bridge.changed.emit()
            settings.setProperty('selectedAccessorySubject', subject)
            pump(80)
            assert window.grabWindow().save(str(output.with_name('mascot-' + themes[subject] + '.png')))
        bridge._lesson = {**preview_lesson, 'subject': 'Môn riêng'}
        bridge.changed.emit()
        settings.setProperty('selectedAccessorySubject', 'Môn riêng')
        pump(20)
        assert control('mascotPreview').property('subject') == 'Môn riêng'
        control('mascotAccessories').setProperty('checked', False)
        assert not control('mascotPreview').property('themed')
        assert library.get(preview_lesson['id'])['subject'] == 'Vật lý', 'Preview must not edit the saved lesson'
        assert not warnings, warnings
        result.update(status='passed', preset_playback_seconds=latencies,
                      save_during_preview_seconds=saved_seconds,
                      max_ui_tick_gap_seconds=max((b-a for a,b in zip(beats, beats[1:])), default=0),
                      saved_preference=library.setting('voice_options', {}),
                      late_cancelled_playback=False, model_inference=False,
                      subject_count=len(themes), subject_themes=themes, qml_warnings=warnings)
    except Exception:
        result['error'] = traceback.format_exc()
    finally:
        timer.stop()
        if window is not None:
            window.close()
        if bridge is not None:
            bridge.voice_controls.shutdown()
            bridge.slidePreview.shutdown()
            bridge.narration_preparation.shutdown()
            bridge.english_reader.shutdown()
            bridge.browserAI.shutdown()
            bridge.classroom.shutdown()
            bridge._catalog.shutdown()
        if engine is not None:
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
        if library is not None:
            library.close()
        speech.play, voice_preview.preview, speech._vieneu_engine = old_play, old_preview, old_engine
        workspace.cleanup()
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if result['status'] == 'passed' else 1
