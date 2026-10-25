"""Disposable native Qt Word/failover workflow. No teacher files or live API."""

import json
import sys
import tempfile
from pathlib import Path
from threading import Event
from unittest.mock import patch

from docx import Document
from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.alternative_translation import TRANSPORTS, AlternativeStore
from app.branding import configure_application
from app.google_translation import KeyStore, TranslationProblem
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
    report = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/rc169-word-qt')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-word-', ignore_cleanup_errors=True) as temporary:
        directory = Path(temporary)
        library = Library(directory / 'data')
        KeyStore(library.directory).add('AIza' + 'a' * 35)
        AlternativeStore(library.directory, 'languageapp').configure('fixture_translation_1234567890',
            'https://script.google.com/macros/s/' + 'A' * 40 + '/exec')
        original_key = KeyStore(library.directory).path.read_bytes()
        bridge = Bridge(library)
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
        blocked = [False]

        def c(name):
            return control(window, name)

        def fake_google(*_):
            calls.append('google')
            raise TranslationProblem('api_network', 'Dịch vụ tạm chưa dùng được.')

        def fake_languageapp(rows, *_):
            calls.append('languageapp')
            if blocked[0]:
                entered.set()
                assert release.wait(20)
            return [row.replace('Vật có ', 'The object has a ') for row in rows]

        try:
            until(lambda: bridge.googleSettings.ready)
            with patch('app.translation_knowledge.lookup', return_value=None), patch('app.google_translation.request', fake_google), patch.dict(TRANSPORTS, languageapp=fake_languageapp):
                # Constructor's default Google transport is already bound; replace it explicitly.
                from app.google_translation import Translator

                real_send = Translator._send
                with patch.object(Translator, '_send', lambda self, rows, credential, source, target:
                                  fake_google(rows) if not hasattr(self, 'provider') else real_send(self, rows, credential, source, target)):
                    document = Document()
                    document.add_heading('Bài học chuyển động', 0)
                    document.add_paragraph('Vật có vận tốc 12 m/s.')
                    document.add_paragraph('😀 Vật có vận tốc 13 m/s.')
                    document.add_paragraph('Giữ nguyên phần không được chọn.')
                    source = directory / 'Bài chuyển động.docx'
                    document.save(source)
                    original = source.read_bytes()
                    window.setProperty('page', 'new')
                    click(window, c('conversionDocumentWord'))
                    assert window.property('page') == 'word'
                    bridge.wordDocuments.openFile(source.as_uri())
                    until(lambda: not bridge.busy and bridge.wordDocuments.state['id'])
                    pump(120)
                    assert not warnings, warnings
                    assert window.grabWindow().save(str(report / 'word-loaded.png'))
                    click(window, c('wordSelect_1'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 1
                    # Select precisely after an emoji; Qt offsets are UTF-16.
                    text = c('wordSourceText_2')
                    click(window, text)
                    end = len(text.property('text').encode('utf-16-le')) // 2
                    assert QMetaObject.invokeMethod(text, 'select', Q_ARG(int, 3), Q_ARG(int, end))
                    pump(20)
                    assert text.property('selectedText'), (text.property('text'), text.property('selectionStart'), text.property('selectionEnd'))
                    click(window, c('wordAddRange_2'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 2
                    c('wordSubject').setProperty('currentIndex', bridge.conversionSubjects.index('Vật lý'))
                    click(window, c('wordPreview'))
                    until(lambda: not bridge.busy, timeout=30)
                    assert bridge.wordDocuments.state['phase'] == 'review', bridge.wordDocuments.state['message']
                    assert calls == ['google', 'languageapp'], calls
                    assert window.grabWindow().save(str(report / 'word-review.png'))
                    region = bridge.wordDocuments.state['regions'][0]
                    bridge.wordDocuments.setDraft(region['id'], region['display_en'].replace('has a velocity', 'has a velocity of'))
                    click(window, c('wordSave'))
                    until(lambda: not bridge.busy)
                    state = bridge.wordDocuments.state
                    assert state['phase'] == 'completed', state['message']
                    assert not bridge.message, 'A completed Word task must not leave the global processing message active'
                    assert source.read_bytes() == original
                    assert Path(state['export_path']).is_file()
                    output_sha = state['output_sha256']
                    for theme in ('light', 'dark'):
                        bridge.setApplicationTheme(theme)
                        for width, height in ((1080, 700), (1366, 850)):
                            window.resize(width, height)
                            pump(100)
                            save = c('wordOpenOutput')
                            rect = save.mapRectToScene(save.boundingRect())
                            assert rect.bottom() <= window.height() and rect.right() <= window.width(), rect
                            assert window.grabWindow().save(str(report / f'word-{theme}-{width}.png'))
                    window.resize(1366, 850)
                    click(window, c('wordGoLibrary'))
                    until(lambda: not bridge.busy)
                    assert window.property('page') == 'library' and window.property('libraryGroup') == 'word'
                    assert len(bridge.wordDocuments.library) == 1
                    assert library.list_lessons() == [], 'Word must not enter the PowerPoint library'
                    assert window.grabWindow().save(str(report / 'word-library.png'))
                    identity = state['id']
                    bridge.wordDocuments.loadRecord(identity)
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['output_sha256'] == output_sha
                    for mode_index in (1, 3, 2):
                        c('wordMode').setProperty('currentIndex', mode_index)
                        click(window, c('wordPreview'))
                        until(lambda: not bridge.busy, timeout=30)
                        assert bridge.wordDocuments.state['phase'] == 'review', bridge.wordDocuments.state['message']
                        if mode_index == 2:
                            first = bridge.wordDocuments.state['regions'][0]
                            assert first['annotations']
                            bridge.wordDocuments.setKeywordDraft(first['id'], 0, 'speed')
                        pump(120)  # The completed-state footer has just gained the Save action again.
                        click(window, c('wordSave'))
                        until(lambda: not bridge.busy)
                        assert bridge.wordDocuments.state['phase'] == 'completed', bridge.wordDocuments.state['message']
                        assert window.grabWindow().save(str(report / f'word-mode-{mode_index}.png'))
                    assert source.read_bytes() == original
                    first = bridge.wordDocuments.state['regions'][0]
                    bridge.wordDocuments.setKeywordDraft(first['id'], 0, 'discarded draft')
                    bridge.wordDocuments.removeRange(first['id'])
                    until(lambda: not bridge.busy)
                    bridge.wordDocuments.preview(dict(mode='keywords'), 'Vật lý', '11')
                    until(lambda: not bridge.busy, timeout=30)
                    assert bridge.wordDocuments.state['phase'] == 'review', bridge.wordDocuments.state['message']
                    bridge.wordDocuments.restorePrevious()
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['phase'] == 'completed'
                    assert c('wordMode').property('currentIndex') == 3, 'Undo must also restore the visible mode control'
                    # New source, pending request: Stop must retain the input and checkpoint.
                    document = Document()
                    document.add_paragraph('Vật có vận tốc 14 m/s.')
                    stop_source = directory / 'Bài dừng tiếp tục.docx'
                    document.save(stop_source)
                    bridge.wordDocuments.openFile(stop_source.as_uri())
                    until(lambda: not bridge.busy)
                    bridge.wordDocuments.selectAll('paragraphs')
                    until(lambda: not bridge.busy)
                    blocked[0] = True
                    bridge.wordDocuments.preview(dict(mode='below'), 'Vật lý', '11')
                    until(entered.is_set, timeout=30)
                    bridge.wordDocuments.stop()
                    release.set()
                    until(lambda: not bridge.busy, timeout=30)
                    assert bridge.wordDocuments.state['phase'] == 'paused'
                    assert not bridge.wordDocuments.state['working']
                    used = len(calls)
                    bridge.wordDocuments.preview(dict(mode='below'), 'Vật lý', '11')
                    until(lambda: not bridge.busy, timeout=30)
                    assert bridge.wordDocuments.state['phase'] == 'review', bridge.wordDocuments.state['message']
                    assert len(calls) == used, 'Resume must reuse the result cached while Stop was requested'
                    click(window, c('wordTabPowerPoint'))
                    assert window.property('page') == 'new'
                    assert c('creationSourceArea').isVisible()
                    assert KeyStore(library.directory).path.read_bytes() == original_key
                    assert not warnings, warnings
            result = dict(status='passed', api='fixture only', checks=[
                'Native Word tab; paragraph checkbox and disjoint text selection after emoji',
                'Primary provider fails; configured fallback succeeds; original key unchanged',
                'Editable review; save retains completion; source unchanged',
                'Light/dark at 1080 and 1366; save control reachable; zero QML warnings',
                'Word shares the library with PowerPoint while retaining independent storage; reopen keeps the result',
                'All four modes export; keyword edit and undo keep matching review metadata',
                'Stop while an HTTP fixture is pending retains source/selection; Resume reuses completed chunks',
                'Return to PowerPoint keeps its source workflow'], calls=calls, qml_warnings=warnings,
                output_sha256=output_sha)
            (report / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False))
        finally:
            release.set()
            window.close()
            for component in (bridge.batchQueue, bridge.slidePreview, bridge.googleSettings, bridge._library_preferences,
                              bridge._catalog, bridge.classroom, bridge.libraryThumbnails, bridge.voice_controls,
                              bridge.browserAI, bridge.english_reader, bridge.narration_preparation, bridge.inputDocuments):
                component.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
