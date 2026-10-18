"""Real Qt + local PowerPoint; API fixture only, no keys or teacher data sent."""
import json
import tempfile
import time
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from PySide6.QtCore import QCoreApplication, QEvent, QEventLoop, QPointF, Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app import google_conversion
from app.branding import configure_application
from app.google_translation import Translator
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def pump(ms=30):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def until(check, timeout=120):
    end = time.monotonic() + timeout
    while not check():
        assert time.monotonic() < end, 'Google Qt flow timed out'
        pump()


app = QGuiApplication([])
configure_application(app)
QQuickStyle.setStyle('Basic')
for path in (RESOURCE_ROOT / 'assets').glob('*.ttf'):
    QFontDatabase.addApplicationFont(str(path))
app.setFont(QFont('Be Vietnam Pro', 10))
reports = Path('reports/google-api')
reports.mkdir(parents=True, exist_ok=True)
calls = []


def transport(texts, key, source, target):
    calls.append(len(texts))
    time.sleep(1.3)  # allow the real clock/controls to update during the request
    return [text.replace('Cơ năng', 'Mechanical energy').replace('Vật có vận tốc', 'The object has a velocity of') for text in texts]


google_conversion.Translator = lambda directory, budget: Translator(directory, budget, transport=transport)
with tempfile.TemporaryDirectory(prefix='biliclass-google-ui-', ignore_cleanup_errors=True) as directory:
    directory = Path(directory)
    source = directory / 'source.pptx'
    deck = Presentation()
    deck.slide_width, deck.slide_height = Inches(13.333), Inches(7.5)
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    for text, y, h, size in [('Cơ năng', .4, 1, 32), ('Vật có vận tốc 12 m/s.', 2, 4, 24)]:
        box = slide.shapes.add_textbox(Inches(.6), Inches(y), Inches(12), Inches(h))
        box.text = text
        box.text_frame.paragraphs[0].font.size = Pt(size)
        box.text_frame.paragraphs[0].font.name = 'Arial'
    deck.save(source)
    library = Library(directory / 'library')
    library.set_setting('chatgpt_request_folder', 'old-browser-job-must-not-run')
    bridge = Bridge(library)
    bridge._browser_ai.signIn = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('Browser must stay disabled'))
    assert bridge.googleTranslation and not bridge._browser_ai._health_timer.isActive()
    assert not bridge.chatgptRequest
    assert [row['id'] for row in bridge.conversionFormats] == ['parallel_columns','english_only']
    warnings = []
    engine = QQmlApplicationEngine()
    engine.warnings.connect(lambda rows: warnings.extend(str(row) for row in rows))
    engine.rootContext().setContextProperty('bridge', bridge)
    engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
    assert engine.rootObjects(), warnings
    window = engine.rootObjects()[0]
    window.resize(1366, 850)

    def control(name):
        queue = [window.contentItem()]
        while queue:
            item = queue.pop()
            if item.objectName() == name:
                return item
            queue.extend(item.childItems())
        raise AssertionError(name)

    def click(name):
        item = control(name)
        parent = item.parentItem()
        while parent is not None:
            if parent.metaObject().indexOfProperty('contentY') >= 0:
                top = item.mapToItem(parent, QPointF(0, 0)).y()
                bottom = item.mapToItem(parent, QPointF(0, item.height())).y()
                if bottom > parent.height() or top < 0:
                    parent.setProperty('contentY', max(0, min(parent.property('contentHeight') - parent.height(),
                        parent.property('contentY') + top - 100)))
                    pump(100)
            parent = parent.parentItem()
        point = item.mapToScene(QPointF(item.width()/2, item.height()/2)).toPoint()
        assert item.isVisible() and item.isEnabled(), name
        assert 0 <= point.y() < window.height(), (name, point)
        QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
        pump(70)

    bridge.navigate.connect(lambda page: window.setProperty('page', 'settings' if page == 'browser-settings' else page))
    window.setProperty('page', 'settings')
    pump(200)
    click('settingsTab6')
    assert not control('browserServiceChatGPT').isVisible()
    assert not control('browserServiceGemini').isVisible()
    control('googleApiKeys').setProperty('text', 'Project A | ' + 'AIza' + 'a'*35 + '\nProject B | ' + 'AIza' + 'b'*35)
    click('saveGoogleApiKeys')
    assert not control('googleApiKeys').property('text')
    assert len(bridge.googleSettings.state['keys']) == 2
    assert window.grabWindow().save(str(reports / 'settings.png'))
    beats = []
    timer = QTimer()
    timer.setInterval(50)
    timer.timeout.connect(lambda: beats.append(time.monotonic()))
    timer.start()
    bridge.convertDocument('Cơ năng', 'Vật lý', 'THPT', '11', '', QUrl.fromLocalFile(str(source)).toString(),
                           'parallel_columns', 'standard', 'source')
    until(lambda: calls)
    assert bridge.browserState['running']
    pump(1100)
    assert bridge.conversionClock['seconds'] >= 1
    assert control('browserConversionPercent').property('text').endswith('%')
    assert window.grabWindow().save(str(reports / 'loading.png'))
    until(lambda: bridge._lesson and not bridge._busy)
    lesson = bridge._lesson
    assert lesson['external_deck']['provider'] == 'google_translate'
    assert lesson['narration']['mode'] == 'none'
    assert bridge.browserState['phase'] == 'completed'
    until(lambda: not bridge._busy)
    output = directory / 'download.pptx'
    bridge.exportPowerPoint(QUrl.fromLocalFile(str(output)).toString())
    until(lambda: not bridge._busy)
    assert output.is_file() and len(Presentation(output).slides) == 1
    assert calls == [2]
    assert all('key' not in row for row in bridge.googleSettings.state['keys'])
    for size in [(1366, 850), (1080, 700)]:
        window.resize(*size)
        window.setProperty('page', 'settings')
        pump(150)
        assert window.grabWindow().save(str(reports / f'settings-{size[0]}.png'))
    timer.stop()
    assert len(beats) > 10, 'UI timer did not keep ticking'
    assert not warnings, warnings
    result = {'status': 'passed', 'api': 'fixture; not a live Google benchmark', 'api_calls': len(calls),
              'checks': ['multi-key save and clear', 'browser controls hidden; no startup browser job',
                         'native source → text API → local editable PPTX', 'clock and percentage during request',
                         'separate voice step; download without voice', 'two window sizes; no QML warnings'],
              'qml_warnings': warnings, 'max_ui_gap_seconds': round(max(b-a for a,b in zip(beats, beats[1:])), 3)}
    (reports / 'qt-flow.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    window.close()
    bridge.slidePreview.shutdown()
    bridge._catalog.shutdown()
    bridge.classroom.shutdown()
    bridge.libraryThumbnails.shutdown()
    bridge.voice_controls.shutdown()
    engine.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    app.processEvents()
    bridge.browserAI.shutdown()
    bridge.english_reader.shutdown()
    bridge.narration_preparation.shutdown()
    library.close()
