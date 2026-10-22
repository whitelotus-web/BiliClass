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
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/rc64/scroll')
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-scroll-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        for index in range(25):
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
            until(lambda: len(bridge.lessons) == 25 and bridge._catalog.worker is None)
            for width, height in ((1080, 700), (1366, 850), (1680, 960)):
                window.resize(width, height)
                pages = [('library', 'libraryHomeScroll'), ('new', 'creationScroll'),
                                   ('result', 'resultScroll'),
                                   ('settings', 'settingsContentScroll'), ('reference', 'termsScroll')]
                if bridge.experimentalTeaching:
                    pages += [('classroom', 'classroomPage'), ('reports', 'reportContentScroll')]
                for page, name in pages:
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
                    # Windows may adjust the requested minimum width for its
                    # native frame. Test against the real client area.
                    assert bar.mapToScene(QPointF(bar.width(), 0)).x() <= window.width() - 1, name
                    if bar.isVisible():
                        assert abs(bar.property('contentItem').width() - 6) < .2, name
                    if page in ('new', 'library') and bar.isVisible():
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
                flick = c('libraryHomeScroll').property('contentItem')
                for page_number in (2, 1):
                    flick.setProperty('contentY', max(0, flick.property('contentHeight')-flick.height()))
                    window.setProperty('libraryPage', page_number)
                    pump(120)
                    assert abs(flick.property('contentY')) < 1, 'A new page must start with its first result'
                flick.setProperty('contentY', max(0, flick.property('contentHeight')-flick.height()))
                bridge.setLessonOrder('created_desc' if bridge.lessonOrder == 'title_asc' else 'title_asc')
                pump(120)
                assert abs(flick.property('contentY')) < 1, 'A new sort order must start at the top'
                flick.setProperty('contentY', max(0, flick.property('contentHeight')-flick.height()))
                c('librarySearch').setProperty('text', 'bài thử')
                pump(120)
                assert abs(flick.property('contentY')) < 1, 'A new search must show the first match'
                c('librarySearch').setProperty('text', 'khong-co-bai-phu-hop')
                pump(120)
                if c('libraryScrollBar').isVisible():
                    result = window.property('libraryResult')
                    result = result.toVariant() if hasattr(result, 'toVariant') else result
                    flick = c('libraryHomeScroll').property('contentItem')
                    (out/'empty-search-debug.json').write_text(json.dumps(dict(
                        total=result['total'], contentY=flick.property('contentY'),
                        contentHeight=flick.property('contentHeight'), height=flick.height(),
                        barSize=c('libraryScrollBar').property('size'),
                        items=[dict(name=item.objectName(), height=item.height(), implicit=item.implicitHeight(),
                                    children=[dict(name=c.objectName(), height=c.height(), implicit=c.implicitHeight(),
                                                   visible=c.isVisible()) for c in item.childItems()])
                               for item in flick.property('contentItem').childItems()])), encoding='utf-8')
                    window.grabWindow().save(str(out/'empty-search-debug.png'))
                assert not c('libraryScrollBar').isVisible()
                assert c('libraryHomeScroll').property('availableWidth') == before
                c('librarySearch').setProperty('text', '')
                pump(100)
                bridge.setLibraryView('grid')
                pump(120)
                c('librarySearch').setProperty('text', 'khong-co-bai-phu-hop')
                pump(120)
                assert not c('libraryScrollBar').isVisible(), 'An empty grid must not retain the previous grid height'
                c('librarySearch').setProperty('text', '')
                bridge.setLibraryView('list')
                pump(120)

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
                      'checks': ['page gutters across active screens and three sizes', '6px thumb; 18px pointer target',
                                 'search, sort and pagination start at first result; empty list/grid shrink without stale scroll height',
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
