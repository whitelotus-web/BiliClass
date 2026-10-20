"""Verify submission UI scope and reversible development mode on one fixture."""

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.teaching_session import prepare_teaching
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tests'))
from test_teaching_session import prepared_lesson


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    reports = Path('reports/rc101/submission-scope')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-submission-', ignore_cleanup_errors=True) as folder:
        lesson, preview, directory, source = prepared_lesson(Path(folder))
        source_before = source.read_bytes()
        audio_before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (directory/'audio').glob('*.wav')}
        for enabled in (False, True):
            with patch.dict(os.environ, BILICLASS_EXPERIMENTAL_TEACHING='1' if enabled else '0'):
                library = Library(directory)
                bridge = Bridge(library)
                assert bridge.experimentalTeaching is enabled
                engine = QQmlApplicationEngine()
                warnings = []
                engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
                engine.rootContext().setContextProperty('bridge', bridge)
                engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
                assert engine.rootObjects(), warnings
                root = engine.rootObjects()[0]
                companion = control(root, 'companionWindow')

                def c(name):
                    return control(root, name)

                def exists(name):
                    try:
                        c(name)
                        return True
                    except AssertionError:
                        return False

                try:
                    pump(180)
                    assert exists('navigationclassroom') is enabled
                    assert exists('settingsTab4') is enabled
                    root.setProperty('page', 'classroom')
                    pump(100)
                    assert root.property('page') == ('classroom' if enabled else 'home')
                    root.setProperty('page', 'reports')
                    pump(100)
                    assert root.property('page') == ('reports' if enabled else 'home')
                    root.setProperty('page', 'settings')
                    settings = c('settingsPage')
                    settings.setProperty('activeTab', 4)
                    pump(100)
                    assert settings.property('activeTab') == (4 if enabled else 0)
                    for width, height in ((1080, 700), (1366, 850)):
                        root.resize(width, height)
                        settings.setProperty('activeTab', 0)
                        pump(120)
                        assert root.grabWindow().save(str(reports/f'settings-{int(enabled)}-{width}.png'))
                    bridge._show_lesson(lesson, preview, destination='voice', auto_repair=False, load_preview=False)
                    bridge.teaching_session.bind(prepare_teaching(lesson, preview, directory))
                    companion.setProperty('collapsed', False)
                    bridge.showCompanion(companion)
                    pump(150)
                    assert c('companionExplain').isVisible() is enabled
                    assert c('companionAssistantToggle').isVisible() is enabled
                    assert c('companionSettings').isVisible() and c('hideCompanion').isVisible()
                    assert c('companionNext').isVisible() and c('companionPrevious').isVisible()
                    assert companion.grabWindow().save(str(reports/f'mascot-{int(enabled)}.png'))
                    root.setProperty('page', 'editor')
                    pump(100)
                    assert c('teachingButton').isVisible() is enabled
                    assert c('readinessButton').isVisible() is enabled
                    if not enabled:
                        c('helpDialog').open()
                        pump(100)
                        visible_text = '\n'.join(str(item.property('text') or '') for item in c('helpDialog').findChildren(QQuickItem) if item.isVisible())
                        assert not any(word in visible_text for word in ('Quiz', 'quét QR', 'Trợ giảng &', 'đang phát triển'))
                        c('helpDialog').close()
                    assert library.get(lesson['id'])['narration'] == lesson['narration']
                    assert not warnings, warnings
                finally:
                    for worker in (bridge.googleSettings, bridge._library_preferences, bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                                   bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                                   bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                        worker.shutdown()
                    companion.setProperty('disposing', True)
                    companion.hide()
                    root.hide()
                    engine.deleteLater()
                    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
                    app.processEvents()
                    library.close()
        assert source.read_bytes() == source_before
        assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (directory/'audio').glob('*.wav')} == audio_before
        result = dict(status='passed', qml_warnings=[], checks=[
            'Submission hides sidebar/Home/classroom settings, reports routes and four assistant actions',
            'Presentation, previous/next, speaker controls, settings and hide remain available',
            'Help and mascot examples describe only submitted features',
            'Development override restores entry points without rewriting lesson/voice data'])
        (reports/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
