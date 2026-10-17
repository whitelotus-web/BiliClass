"""Real Qt geometry and pointer checks for page gutters and compact editors."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QCoreApplication, QEvent, QPoint, QPointF, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from qt_result_preview_mascot_smoke import control, pump, until

from app.branding import configure_application
from app.google_translation import KeyStore
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def drag_and_wheel(window, scroll):
    bar = control(window, scroll.property('barObjectName'))
    flick = scroll.property('contentItem')
    flick.setProperty('contentY', 0)
    pump(80)
    assert bar.isVisible() and bar.property('size') < 1
    thumb = bar.property('contentItem')
    start = thumb.mapToScene(QPointF(thumb.width() / 2, thumb.height() / 2)).toPoint()
    QTest.mouseMove(window, start)
    QTest.mousePress(window, Qt.LeftButton, Qt.NoModifier, start)
    QTest.mouseMove(window, start + QPoint(0, 75), 40)
    QTest.mouseRelease(window, Qt.LeftButton, Qt.NoModifier, start + QPoint(0, 75))
    pump(120)
    overflow = flick.property('contentHeight') - flick.height()
    assert flick.property('contentY') > min(20, overflow / 4), (scroll.objectName(), window.width(),
                                                            flick.property('contentY'), overflow)
    flick.setProperty('contentY', 0)
    pump(80)
    point = scroll.mapToScene(QPointF(scroll.property('availableWidth') - 3, scroll.height() / 2))
    QTest.mouseMove(window, point.toPoint())
    QTest.wheelEvent(window, point, QPoint(0, -360))
    pump(200)
    assert flick.property('contentY') > 0, 'Wheel must still work over page content'
    flick.setProperty('contentY', 0)
    pump(80)


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    out = Path('reports/rc64/scroll')
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-scroll-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        for index in range(12):
            library.create(f'Bài thử {index + 1}: Dao động điều hòa', 'Vật lý', 'THPT', '11', [('Slide 1', 'Vận tốc biến thiên.')])
        KeyStore(Path(folder)).add('AIza' + 'a' * 35)
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(value) for value in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        def c(name):
            return control(window, name)
        measurements = []
        compact = None
        try:
            until(lambda: len(bridge.lessons) == 12 and bridge._catalog.worker is None)
            for width, height in ((1080, 700), (1366, 850), (1680, 960)):
                window.resize(width, height)
                for page, name in [('library', 'libraryHomeScroll'), ('new', 'creationScroll'),
                                   ('chatgpt', 'conversionProgressScroll'), ('result', 'resultScroll'),
                                   ('settings', 'settingsContentScroll'), ('classroom', 'classroomPage'),
                                   ('reports', 'reportContentScroll'), ('reference', 'termsScroll')]:
                    window.setProperty('page', page)
                    pump(150)
                    scroll = c(name)
                    assert scroll.isVisible(), name
                    assert scroll.property('outerGutter'), name
                    assert not scroll.property('clip'), 'Only the viewport should clip an outer scrollbar'
                    bar = c(scroll.property('barObjectName'))
                    assert not c(scroll.property('barObjectName') + 'Horizontal').isVisible(), name
                    edge = scroll.mapToScene(QPointF(scroll.width(), 0)).x()
                    left = bar.mapToScene(QPointF()).x()
                    assert abs(left - edge - 6) < .2, (name, left, edge)
                    assert bar.mapToScene(QPointF(bar.width(), 0)).x() <= width - 1, name
                    if bar.isVisible():
                        assert abs(bar.property('contentItem').width() - 6) < .2, name
                    if page in ('new', 'library'):
                        drag_and_wheel(window, scroll)
                    if page == 'new':
                        assert bar.mapToScene(QPointF(0, bar.height())).y() < c('createLessonButton').mapToScene(QPointF()).y()
                        assert window.grabWindow().save(str(out / f'conversion-{width}.png'))
                    if page == 'settings':
                        settings = c('settingsContentScroll').parentItem()
                        while settings.metaObject().indexOfProperty('activeTab') < 0:
                            settings = settings.parentItem()
                        for tab in (3, 6):
                            settings.setProperty('activeTab', tab)
                            pump(150)
                            assert c(scroll.property('barObjectName')) == bar
                        settings.setProperty('activeTab', 0)
                    if page != 'library':
                        assert not c('libraryScrollBar').isVisible(), 'Hidden page must hide its detached bar'
                    measurements.append({'width': width, 'page': page, 'gutter': round(left - edge, 2)})

                window.setProperty('page', 'library')
                pump(100)
                before = c('libraryHomeScroll').property('availableWidth')
                c('librarySearch').setProperty('text', 'khong-co-bai-phu-hop')
                pump(120)
                assert not c('libraryScrollBar').isVisible()
                assert c('libraryHomeScroll').property('availableWidth') == before
                c('librarySearch').setProperty('text', '')

            component = QQmlComponent(engine)
            component.setData(b'''import QtQuick
import QtQuick.Controls
ApplicationWindow { width: 520; height: 300; visible: true
    ContentScrollView { objectName: "compactScroll"; anchors.fill: parent; anchors.margins: 16
        TextArea { objectName: "compactText"; wrapMode: TextEdit.Wrap; selectByMouse: true
            text: ("Long editable line to check the right edge and caret.\\n").repeat(60) }
    }
}''', QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/ScrollFixture.qml')))
            compact = component.create()
            assert compact, [error.toString() for error in component.errors()]
            pump(150)
            scroll = control(compact, 'compactScroll')
            bar = control(compact, scroll.property('barObjectName'))
            assert not control(compact, scroll.property('barObjectName') + 'Horizontal').isVisible()
            flick = scroll.property('contentItem')
            left = bar.mapToScene(QPointF()).x()
            assert flick.mapToScene(QPointF(flick.width(), 0)).x() <= left - 5
            drag_and_wheel(compact, scroll)
            text = control(compact, 'compactText')
            text.setProperty('cursorPosition', len(text.property('text')))
            pump(150)
            assert flick.property('contentY') > 0, 'Caret at end of long text must stay reachable'
            text.setProperty('text', 'Nội dung ngắn')
            pump(150)
            assert not bar.isVisible()
            assert scroll.property('rightPadding') == 24, 'Reserve space even when the thumb hides'
            text.setProperty('wrapMode', 0)
            text.setProperty('text', 'Long unwrapped input ' * 80)
            pump(150)
            horizontal = control(compact, scroll.property('barObjectName') + 'Horizontal')
            assert horizontal.isVisible() and horizontal.width() > 400
            assert flick.mapToScene(QPointF(0, flick.height())).y() <= horizontal.mapToScene(QPointF()).y()
            assert abs(horizontal.property('contentItem').height() - 6) < .2
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings, 'measurements': measurements,
                      'checks': ['page gutters across eight screens and three sizes', '6px thumb; 18px pointer target',
                                 'drag and wheel on conversion/library/compact text', 'conversion footer stays outside bar',
                                 'settings tabs share gutter', 'hidden page bars and no width jump',
                                 'compact editor viewport/caret stays clear of bar', 'unwrapped text reserves horizontal gutter']}
            (out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            if compact is not None:
                compact.close()
                compact.deleteLater()
            window.close()
            for worker in (bridge.libraryThumbnails, bridge.slidePreview, bridge._catalog, bridge.browserAI,
                           bridge.english_reader, bridge.narration_preparation, bridge.classroom, bridge.voice_controls):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
