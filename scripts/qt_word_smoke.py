"""Disposable native Qt Word/failover workflow. No teacher files or live API."""

import io
import json
import sys
import tempfile
from pathlib import Path
from threading import Event
from unittest.mock import patch

from docx import Document
from docx.shared import Inches
from PIL import Image
from PySide6.QtCore import (
    Q_ARG,
    Q_RETURN_ARG,
    QCoreApplication,
    QEvent,
    QMetaObject,
    QPointF,
    QRectF,
    Qt,
    QUrl,
)
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

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
        window.requestActivate()
        until(window.isActive)
        entered, release = Event(), Event()
        calls = []
        opened_urls = []
        blocked = [False]

        def c(name):
            return control(window, name)

        def check_formatting_row():
            picker = 'wordKeywordDensity' if c('wordMode').property('currentIndex') == 2 else 'wordEnglishColor'
            parts = [c(name) for name in ('wordMode', picker, 'wordTextStyle', 'wordOriginalFont', 'wordEnglishFont')]
            rectangles = [item.mapRectToScene(item.boundingRect()) for item in parts]
            assert max(rect.top() for rect in rectangles) - min(rect.top() for rect in rectangles) < 3, rectangles
            assert all(left.right() <= right.left() + 1 for left, right in zip(rectangles, rectangles[1:])), rectangles
            toolbar = c('wordFormattingToolbar').mapRectToScene(c('wordFormattingToolbar').boundingRect())
            assert rectangles[-1].right() <= toolbar.right() + 1 <= window.width(), rectangles[-1]

        def plain_text(text):
            return QMetaObject.invokeMethod(text, 'getText', Qt.DirectConnection, Q_RETURN_ARG(str),
                Q_ARG(int, 0), Q_ARG(int, text.property('length'))).replace('\u2029', '\n')

        def preview_text():
            return plain_text(c('wordContinuousText'))

        def drag_text(start, end):
            text = c('wordContinuousText')

            def point(position):
                rect = QMetaObject.invokeMethod(text, 'positionToRectangle', Qt.DirectConnection,
                    Q_RETURN_ARG(QRectF), Q_ARG(int, position))
                return text.mapToScene(QPointF(rect.x(), rect.center().y())).toPoint()

            first, last = point(start), point(end)
            QTest.mouseMove(window, first)
            pump(30)
            # Advance QTest's simulated input timestamp, too. A real-time event
            # loop wait alone can turn repeated drags into double/triple clicks.
            QTest.mousePress(window, Qt.LeftButton, Qt.NoModifier, first,
                QGuiApplication.styleHints().mouseDoubleClickInterval() + 40)
            pump(20)
            for step in range(1, 6):
                QTest.mouseMove(window, first + (last - first) * (step / 5), 20)
            assert not c('wordHighlightPopup').property('visible'), 'Confirmation must wait for mouse release'
            QTest.mouseRelease(window, Qt.LeftButton, Qt.NoModifier, last)
            until(lambda: c('wordHighlightPopup').property('visible'))
            # At an end-of-line Qt may include the adjacent paragraph separator
            # when the caret rectangle is rounded to a physical screen pixel.
            expected = preview_text().encode('utf-16-le')[start * 2:end * 2].decode('utf-16-le')
            actual = text.property('selectedText').replace('\u2029', '\n')
            assert actual.strip() == expected.strip(), (actual, expected)

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
            with patch('app.word_ui.QDesktopServices.openUrl', lambda url: opened_urls.append(url.toString()) or True), patch('app.translation_knowledge.lookup', return_value=None), patch('app.google_translation.request', fake_google), patch.dict(TRANSPORTS, languageapp=fake_languageapp):
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
                    assert c('wordConfiguration').isVisible() and c('wordSourceArea').isVisible()
                    assert c('wordConfiguration').mapToScene(c('wordConfiguration').boundingRect().topLeft()).y() > c('wordSourceArea').mapToScene(c('wordSourceArea').boundingRect().topLeft()).y()
                    assert not c('wordSelectAll').isEnabled() and not c('wordPreview').isEnabled()
                    assert not c('wordSave').isVisible() and not c('wordGoLibrary').isVisible()
                    assert c('wordConfigurationSummary').isVisible()
                    assert c('wordTextStyle').property('italic') and not c('wordTextStyle').property('bold')
                    assert c('wordOriginalFont').property('checked') and c('wordEnglishFont').isVisible()
                    assert not c('wordEnglishFont').isEnabled()
                    font_rect = c('wordEnglishFont').mapRectToScene(c('wordEnglishFont').boundingRect())
                    original_rect = c('wordOriginalFont').mapRectToScene(c('wordOriginalFont').boundingRect())
                    assert font_rect.left() >= original_rect.right() and abs(font_rect.top() - original_rect.top()) < 2
                    for choice in range(4):
                        click(window, c('wordMode_' + str(choice)))
                        assert c('wordMode').property('currentIndex') == choice
                        check_formatting_row()
                    radio_rows = [c('wordMode_' + str(index)).mapToScene(QPointF()).y() for index in range(4)]
                    assert max(radio_rows) - min(radio_rows) < 2
                    click(window, c('wordMode_0'))
                    for width, height in ((1080, 700), (1366, 850)):
                        window.resize(width, height)
                        pump(100)
                        for index in (0, 2):
                            c('wordMode').setProperty('currentIndex', index)
                            pump(30)
                            check_formatting_row()
                            assert window.grabWindow().save(str(report / f'word-toolbar-{width}-{index}.png'))
                    c('wordMode').setProperty('currentIndex', 0)
                    assert c('wordEnglishColor').property('colorCode') == 'original'
                    assert c('wordPreview').property('text') == 'Chuyển đổi bài giảng'
                    for level, classes in ((2, ['1', '2', '3', '4', '5']), (1, ['6', '7', '8', '9']), (0, ['10', '11', '12'])):
                        c('wordEducation').setProperty('currentIndex', level)
                        pump(30)
                        assert c('wordGrade').property('model') == classes
                    c('wordGrade').setProperty('currentIndex', 1)
                    click(window, c('wordStyleSubscript'))
                    assert c('wordTextStyle').property('script') == 'subscript'
                    click(window, c('wordStyleSuperscript'))
                    assert c('wordTextStyle').property('script') == 'superscript' and not c('wordStyleSubscript').property('checked')
                    click(window, c('wordStyleSuperscript'))
                    assert c('wordTextStyle').property('script') == 'normal'
                    click(window, c('wordEnglishColor'))
                    assert c('wordColorPalette').property('visible')
                    assert window.grabWindow().save(str(report / 'word-color-palette.png'))
                    click(window, c('wordColor_7030A0'))
                    assert c('wordEnglishColor').property('colorCode') == '7030A0'
                    click(window, c('wordEnglishColor'))
                    click(window, c('wordKeepOriginalColor'))
                    assert c('wordEnglishColor').property('colorCode') == 'original'
                    assert window.grabWindow().save(str(report / 'word-empty.png'))
                    c('wordTitle').setProperty('text', 'Chuyển động đều')
                    c('wordTextStyle').setProperty('bold', True)
                    assert QMetaObject.invokeMethod(c('wordTextStyle'), 'chosen')
                    click(window, c('wordOriginalFont'))
                    assert c('wordEnglishFont').isVisible()
                    c('wordEnglishFont').setProperty('currentIndex', bridge.wordDocuments.fontFamilies.index('Arial'))
                    assert QMetaObject.invokeMethod(c('wordEnglishFont'), 'activated', Q_ARG(int, c('wordEnglishFont').property('currentIndex')))
                    assert QMetaObject.invokeMethod(c('wordEnglishColor'), 'choose', Q_ARG('QVariant', '1667B1'))
                    assert bridge.wordDocuments.formattingDefaults == dict(color='1667B1', font='Arial', italic=True, bold=True, underline=False, strike=False, script='normal')
                    assert window.grabWindow().save(str(report / 'word-custom-font.png'))
                    c('wordSubject').setProperty('currentIndex', bridge.conversionSubjects.index('Vật lý'))
                    c('wordEducation').setProperty('currentIndex', 1)
                    c('wordGrade').setProperty('currentIndex', 0)
                    c('wordMode').setProperty('currentIndex', 1)
                    assert QMetaObject.invokeMethod(c('wordPage'), 'openDocument', Q_ARG('QVariant', source.as_uri()))
                    until(lambda: not bridge.busy and bridge.wordDocuments.state['id'])
                    assert bridge.wordDocuments.state['options']['mode'] == 'columns'
                    assert bridge.wordDocuments.state['subject'] == 'Vật lý' and bridge.wordDocuments.state['grade'] == '6'
                    assert bridge.wordDocuments.state['title'] == 'Chuyển động đều'
                    assert bridge.wordDocuments.state['options']['font'] == 'Arial'
                    click(window, c('wordOriginalFont'))
                    assert c('wordEnglishFont').isVisible() and not c('wordEnglishFont').isEnabled()
                    assert bridge.wordDocuments.sourceFonts
                    assert all(family in c('wordEnglishFont').property('displayText') for family in bridge.wordDocuments.sourceFonts)
                    click(window, c('wordOriginalFont'))
                    assert c('wordEnglishFont').isEnabled() and c('wordEnglishFont').property('currentText') == 'Arial'
                    c('wordEducation').setProperty('currentIndex', 0)
                    c('wordGrade').setProperty('currentIndex', 1)
                    c('wordMode').setProperty('currentIndex', 0)
                    pump(120)
                    assert not warnings, warnings
                    assert window.grabWindow().save(str(report / 'word-loaded.png'))
                    click(window, c('wordShowDocument'))
                    assert c('wordSelectByHighlight').property('checked')
                    assert not c('wordScopeParagraphs').isEnabled() and not c('wordScopeSentences').isEnabled()
                    click(window, c('wordSelectByCheckbox'))
                    assert c('wordScopeParagraphs').isEnabled() and c('wordScopeSentences').isEnabled()
                    click(window, c('wordScopeSentences'))
                    assert c('wordScopeSentences').property('checked')
                    click(window, c('wordScopeParagraphs'))
                    click(window, c('wordSelect_1'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 1
                    # Select precisely after an emoji; Qt offsets are UTF-16.
                    text = c('wordSourceText_2')
                    click(window, text)
                    end = len(plain_text(text).encode('utf-16-le')) // 2
                    assert QMetaObject.invokeMethod(text, 'select', Q_ARG(int, 3), Q_ARG(int, end))
                    pump(20)
                    assert text.property('selectedText'), (text.property('text'), text.property('selectionStart'), text.property('selectionEnd'))
                    click(window, c('wordAddRange_2'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 2
                    # Switching to the continuous view retains checkbox regions. A real drag
                    # through an emoji paragraph offers confirmation only after release.
                    click(window, c('wordSelectByHighlight'))
                    pump(100)
                    assert bridge.wordDocuments.state['selected_count'] == 2
                    content = preview_text()
                    begin = len(content[:content.index('Vật có vận tốc 13')].encode('utf-16-le')) // 2
                    finish = begin + len('Vật có vận tốc 13 m/s.')
                    drag_text(begin, finish)
                    assert calls == [], 'Highlighting must not send text to a provider'
                    assert window.grabWindow().save(str(report / 'word-highlight-popup.png'))
                    click(window, c('wordAcceptHighlight'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 2, 'Duplicate highlights must merge'
                    click(window, c('wordSelectByCheckbox'))
                    pump(80)
                    assert bridge.wordDocuments.state['selected_count'] == 2
                    assert not c('wordHighlightPopup').property('visible')
                    c('wordSubject').setProperty('currentIndex', bridge.conversionSubjects.index('Vật lý'))
                    click(window, c('wordPreview'))
                    until(lambda: not bridge.busy, timeout=30)
                    assert bridge.wordDocuments.state['phase'] == 'completed', bridge.wordDocuments.state['message']
                    assert Path(bridge.wordDocuments.state['export_path']).name == 'Bài chuyển động (Song ngu VI-EN).docx'
                    assert calls == ['google', 'languageapp'], calls
                    assert c('wordSave').isVisible() and c('wordGoLibrary').isVisible()
                    assert not c('wordSave').isEnabled(), 'Automatic save must not offer a redundant save'
                    assert window.grabWindow().save(str(report / 'word-review.png'))
                    region = bridge.wordDocuments.state['regions'][0]
                    bridge.wordDocuments.setDraft(region['id'], region['display_en'].replace('has a velocity', 'has a velocity of'))
                    pump(120)  # Save becomes visible after an automatically saved result.
                    click(window, c('wordSave'))
                    until(lambda: not bridge.busy)
                    state = bridge.wordDocuments.state
                    assert state['phase'] == 'completed', state['message']
                    assert not opened_urls, 'Saving must not accidentally invoke Open Word'
                    assert not bridge.message, 'A completed Word task must not leave the global processing message active'
                    assert source.read_bytes() == original
                    assert Path(state['export_path']).is_file()
                    output_sha = state['output_sha256']
                    for theme in ('light', 'dark'):
                        bridge.setApplicationTheme(theme)
                        for width, height in ((1080, 700), (1366, 850)):
                            window.resize(width, height)
                            pump(100)
                            check_formatting_row()
                            save = c('wordOpenOutput')
                            rect = save.mapRectToScene(save.boundingRect())
                            assert rect.bottom() <= window.height() and rect.right() <= window.width(), rect
                            summary, action = c('wordConfigurationSummary'), c('wordPreview')
                            summary_rect, action_rect = summary.mapRectToScene(summary.boundingRect()), action.mapRectToScene(action.boundingRect())
                            assert action_rect.left() > summary_rect.right() and action_rect.right() <= window.width()
                            assert action_rect.bottom() <= window.height()
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
                        assert bridge.wordDocuments.state['phase'] == 'completed', bridge.wordDocuments.state['message']
                        if mode_index == 2:
                            first = bridge.wordDocuments.state['regions'][0]
                            assert first['annotations']
                            bridge.wordDocuments.setKeywordDraft(first['id'], 0, 'speed')
                            pump(120)
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
                    assert bridge.wordDocuments.state['phase'] == 'completed', bridge.wordDocuments.state['message']
                    bridge.wordDocuments.restorePrevious()
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['phase'] == 'completed'
                    assert c('wordMode').property('currentIndex') == 2, 'Undo must also restore the visible mode control'
                    assert bridge.wordDocuments.state['selected_count'] == 2
                    assert c('wordTitle').property('text') == 'Chuyển động đều'
                    # New source, pending request: Stop must retain the input and checkpoint.
                    document = Document()
                    document.add_paragraph('Vật có vận tốc 14 m/s.')
                    document.add_paragraph('Vật có vận tốc 15 m/s.')
                    stop_source = directory / 'Bài dừng tiếp tục.docx'
                    document.save(stop_source)
                    bridge.wordDocuments.openFile(stop_source.as_uri())
                    until(lambda: not bridge.busy)
                    bridge.wordDocuments.addTextSelection(identity, 0, 5)
                    assert bridge.wordDocuments.state['selected_count'] == 0, 'An old document popup cannot select the new source'
                    assert 'Tài liệu đã đổi' in bridge.wordDocuments.state['message']
                    click(window, c('wordSelectByHighlight'))
                    window.resize(1080, 700)
                    click(window, c('wordShowDocument'))
                    pump(80)
                    count_before_selecting = len(calls)
                    first_end = len('Vật có vận tốc 14 m/s.')
                    drag_text(0, len(preview_text().encode('utf-16-le')) // 2)
                    QTest.keyClick(window, Qt.Key_Escape)
                    pump(40)
                    assert not c('wordHighlightPopup').property('visible')
                    assert bridge.wordDocuments.state['selected_count'] == 0, 'Dismissing confirmation must not select or translate'
                    drag_text(0, len(preview_text().encode('utf-16-le')) // 2)
                    click(window, c('wordAcceptHighlight'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 2, 'A drag can span multiple Word paragraphs'
                    click(window, c('wordClearSelection'))
                    until(lambda: not bridge.busy)
                    drag_text(0, first_end)
                    click(window, c('wordAcceptHighlight'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 1
                    drag_text(first_end + 1, len(preview_text().encode('utf-16-le')) // 2)
                    click(window, c('wordAcceptHighlight'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 2
                    assert len(calls) == count_before_selecting
                    assert window.grabWindow().save(str(report / 'word-highlight-selected.png'))
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
                    assert bridge.wordDocuments.state['phase'] == 'completed', bridge.wordDocuments.state['message']
                    assert len(calls) == used, 'Resume must reuse the result cached while Stop was requested'
                    # Confirm mappings in the actual QML rich-text importer, including
                    # a picture object and repeated table cells (not only plain text).
                    rich = Document()
                    rich.add_heading('Bài học có hình và bảng', 0)
                    picture = io.BytesIO()
                    Image.new('RGB', (160, 80), '#39A6D6').save(picture, format='PNG')
                    picture.seek(0)
                    rich.add_paragraph('Hình minh họa: ').add_run().add_picture(picture, width=Inches(1.4))
                    table = rich.add_table(rows=2, cols=2)
                    for row in table.rows:
                        for cell in row.cells:
                            cell.text = 'Vận tốc 12 m/s.'
                    rich_source = directory / 'Hình và bảng.docx'
                    rich.save(rich_source)
                    bridge.wordDocuments.openFile(rich_source.as_uri())
                    until(lambda: not bridge.busy)
                    window.resize(1366, 850)
                    click(window, c('wordShowDocument'))
                    assert '\ufffc' in preview_text() and preview_text().count('Vận tốc 12 m/s.') == 4
                    from PySide6.QtGui import QTextDocument

                    parsed_preview = QTextDocument()
                    parsed_preview.setHtml(bridge.wordDocuments.previewHtml)
                    (report / 'rich-text-map.json').write_text(json.dumps(dict(native=preview_text(),
                        parsed=parsed_preview.toPlainText()), ensure_ascii=False, indent=2), encoding='utf-8')
                    click(window, c('wordSelectAll'))
                    until(lambda: c('wordHighlightPopup').property('visible'))
                    click(window, c('wordAcceptHighlight'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 6, bridge.wordDocuments.state['message']
                    assert {row['paragraph'] for row in bridge.wordDocuments.state['regions']} == {'p0', 'p1', 'p2', 'p3', 'p4', 'p5'}
                    assert window.grabWindow().save(str(report / 'word-rich-paper.png'))
                    count_before_expanding = len(calls)
                    click(window, c('wordClearAllRanges'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 0
                    click(window, c('wordExpandSource'))
                    until(lambda: c('wordExpandedDialog').property('visible'))
                    pump(100)
                    assert c('wordSourcePanel').parentItem() == c('wordExpandedSourceHost')
                    assert c('wordSourcePanel').width() > window.width() * .8
                    drag_text(0, len('Bài học có hình và bảng'))
                    click(window, c('wordAcceptHighlight'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 1
                    assert window.grabWindow().save(str(report / 'word-expanded-select.png'))
                    click(window, c('wordCollapseSource'))
                    until(lambda: not c('wordExpandedDialog').property('visible'))
                    assert bridge.wordDocuments.state['selected_count'] == 1
                    assert c('wordSourcePanel').parentItem() != c('wordExpandedSourceHost')
                    click(window, c('wordExpandSource'))
                    until(lambda: c('wordExpandedDialog').property('visible'))
                    click(window, c('wordExpandedClearAll'))
                    until(lambda: not bridge.busy)
                    assert bridge.wordDocuments.state['selected_count'] == 0
                    QTest.keyClick(window, Qt.Key_Escape)
                    until(lambda: not c('wordExpandedDialog').property('visible'))
                    assert len(calls) == count_before_expanding, 'Selection and clearing must not contact translation services'
                    for width, height in ((1080, 700), (1366, 850)):
                        window.resize(width, height)
                        click(window, c('wordShowDocument'))
                        click(window, c('wordExpandSource'))
                        until(lambda: c('wordExpandedDialog').property('visible'))
                        pump(50)
                        assert c('wordSourcePanel').mapRectToScene(c('wordSourcePanel').boundingRect()).right() <= window.width()
                        assert window.grabWindow().save(str(report / f'word-expanded-{width}.png'))
                        click(window, c('wordCollapseSource'))
                        until(lambda: not c('wordExpandedDialog').property('visible'))
                    click(window, c('wordTabPowerPoint'))
                    assert window.property('page') == 'new'
                    assert c('creationSourceArea').isVisible()
                    assert KeyStore(library.directory).path.read_bytes() == original_key
                    assert not opened_urls, opened_urls
                    assert not warnings, warnings
            result = dict(status='passed', api='fixture only', checks=[
                'One Word page keeps upload, configuration and document panels; pre-upload choices are retained',
                'Original font/color and italic defaults; custom typography is remembered; editable lesson title restores',
                'Successful conversion automatically saves beside source with the requested suffix; edits remain saveable',
                'Main radio choices; indented square paragraph/sentence choices enabled only in checkbox mode',
                'Word-style color palette, original-color option, typography icons and dependent education/grade choices',
                'Single formatting row: four conversion radios, color/keyword density, typography and original/custom font at laptop and desktop widths',
                'Expanded source workspace: mouse selection, collapse retains ranges, clear-all from both panels, Escape closes',
                'Rich paper preview: native QML selection maps images and repeated table cells to original source ranges',
                'Right-aligned conversion action with selected-configuration summary; Save/library appear after translation',
                'Native Word tab; paragraph checkbox and disjoint text selection after emoji',
                'Mouse drag/release offers confirmation; disjoint highlights accumulate; duplicates merge; switching modes retains selections',
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
