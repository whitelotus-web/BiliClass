"""RC168 opt-in routing UI and Azure batch checkpoint checks with fake HTTP only."""

import hashlib
import json
import sys
import tempfile
from pathlib import Path
from threading import Event
from unittest.mock import patch

from pptx import Presentation
from pptx.util import Inches
from PySide6.QtCore import QCoreApplication, QEvent, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.azure_translation import AzureTranslator
from app.branding import configure_application
from app.google_conversion import load
from app.google_translation import KeyStore
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT / 'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    report = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/rc168-translation')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-provider-', ignore_cleanup_errors=True) as temporary:
        directory = Path(temporary)
        library = Library(directory / 'data')
        KeyStore(library.directory).add('AIza' + 'x' * 35)
        google_file = library.directory / 'translation_api/keys.dpapi'
        original_google = google_file.read_bytes()
        bridge = Bridge(library)
        bridge.previewConvertedSlide = lambda *_: None
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        window.resize(1366, 850)
        window.show()
        entered, release = Event(), Event()
        calls = []

        def c(name):
            return control(window, name)

        def fixture(self, rows, credential, source, target):
            assert credential['key'] == 'a' * 32 and credential['region'] == 'global'
            calls.append(len(rows))
            entered.set()
            assert release.wait(25), 'Fixture was not released'
            return [row.replace('Vật có ', 'The object has a ') for row in rows]

        try:
            until(lambda: bridge.googleSettings.ready)
            window.setProperty('page', 'settings')
            c('settingsPage').setProperty('activeTab', 6)
            pump(100)
            assert c('translationProviderGoogle').property('checked')
            click(window, c('translationProviderAzure'))
            until(lambda: not bridge.busy and bridge.googleSettings.state['provider'] == 'azure')
            assert c('translationProviderAzure').property('checked')
            assert not c('saveGoogleApiKeys').isVisible()
            assert c('azureTranslationCard').isVisible()
            assert not bridge.googleSettings.state['activeConfigured']
            c('azureApiKey').setProperty('text', 'a' * 32)
            c('azureResourceName').setProperty('text', 'Tài nguyên kiểm thử')
            c('azureRegion').setProperty('text', 'global')
            click(window, c('saveAzureTranslation'))
            until(lambda: not bridge.busy)
            assert bridge.googleSettings.state['activeConfigured']
            assert not c('azureApiKey').property('text')
            assert 'a' * 32 not in json.dumps(bridge.googleSettings.state)
            assert google_file.read_bytes() == original_google
            for theme in ('light', 'dark'):
                bridge.setApplicationTheme(theme)
                for width, height in ((1080, 700), (1366, 850)):
                    window.resize(width, height)
                    # Bring the selection card back into the settings viewport.
                    parent = c('translationProviderCard').parentItem()
                    while parent:
                        if parent.metaObject().indexOfProperty('contentY') >= 0:
                            parent.setProperty('contentY', 0)
                        parent = parent.parentItem()
                    pump(100)
                    assert window.grabWindow().save(str(report / f'azure-{theme}-{width}.png'))
            sources = []
            for number in (12, 13):
                deck = Presentation()
                slide = deck.slides.add_slide(deck.slide_layouts[6])
                shape = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(3))
                shape.text = f'Vật có vận tốc {number} m/s.'
                path = directory / f'Thí nghiệm {number}.pptx'
                deck.save(path)
                sources.append(path)
            source_hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in sources]
            assert bridge.batchQueue.selectFiles('convert', [path.as_uri() for path in sources])
            with patch.object(AzureTranslator, '_send', fixture):
                bridge.batchQueue.startConversion(dict(subject='Vật lý', education='THPT', grade='11',
                    format='parallel_columns', preset='standard', style='template'))
                until(entered.is_set, timeout=60)
                assert bridge.batchQueue.running
                assert bridge.batchQueue.state['options']['translation_provider'] == 'azure'
                assert not bridge.googleSettings.chooseProvider('google'), 'Provider switched during work'
                bridge.batchQueue.stop()
                release.set()
                until(lambda: not bridge.busy and not bridge.batchQueue.running, timeout=120)
                assert bridge.batchQueue.state['phase'] == 'paused'
                assert bridge.googleSettings.chooseProvider('google')
                until(lambda: not bridge.busy)
                assert bridge.googleSettings.state['provider'] == 'google'
                assert bridge.batchQueue.state['options']['translation_provider'] == 'azure'
                bridge.batchQueue.resume()
                until(lambda: not bridge.busy and not bridge.batchQueue.running, timeout=180)
            state = bridge.batchQueue.state
            assert state['counts']['done'] == 2 and state['complete'], state
            for row in state['rows']:
                assert load(library.directory, row['folder'])['config']['translation_provider'] == 'azure'
                assert library.get(row['lesson_id'])['external_deck']['translation_provider'] == 'azure'
            assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in sources] == source_hashes
            assert KeyStore(library.directory).public()[0]['used'] == 0
            assert google_file.read_bytes() == original_google
            assert not warnings, warnings
            result = dict(status='passed', api='fixture; no live Azure quality/speed claim', calls=len(calls),
                checks=['Google remains default; original key ciphertext unchanged',
                        'Azure selection, masked save and secret clearing',
                        'light/dark at 1080 and 1366; zero QML warnings',
                        'provider cannot change while work runs',
                        'two real PPTX inputs; stop/resume pins Azure after Settings selects Google',
                        'completion retained; no Google usage; source PPTX unchanged'], qml_warnings=warnings)
            (report / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False))
        finally:
            release.set()
            window.close()
            bridge.batchQueue.shutdown()
            bridge.slidePreview.shutdown()
            bridge.googleSettings.shutdown()
            bridge._library_preferences.shutdown()
            bridge._catalog.shutdown()
            bridge.classroom.shutdown()
            bridge.libraryThumbnails.shutdown()
            bridge.voice_controls.shutdown()
            bridge.browserAI.shutdown()
            bridge.english_reader.shutdown()
            bridge.narration_preparation.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
