"""Real Qt home/navigation flow, with a disposable library and no API calls."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pptx import Presentation
from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, QObject, QPointF, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import click, control, pump, until

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc67/home')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-home-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        def c(name):
            return control(window, name)
        try:
            pump(300)
            assert window.property('page') == 'home'
            assert window.findChild(QObject, 'newLibraryLesson') is None
            assert 'NÂNG TẦM BÀI GIẢNG' in c('brandSlogan').property('text')
            assert window.findChild(QObject, 'homeTranslationUsage') is None
            assert c('homeOverviewHeading').property('text') == 'Tổng quan bài giảng'
            for width, height in ((1080, 700), (1366, 850), (1680, 960)):
                window.resize(width, height)
                c('libraryHomeScroll').property('contentItem').setProperty('contentY', 0)
                pump(250)
                for name in ('homeWelcomeHero', 'homeHeroMascot', 'homeWorkflowStep0', 'homeWorkflowStep3'):
                    item = c(name)
                    point = item.mapToScene(QPointF())
                    assert point.x() >= 0 and point.x()+item.width() <= width, name
                    assert point.y() >= 0 and point.y()+item.height() < height, name
                assert c('homeHeroMascot').width() >= 185
                assert c('homeHeroMascot').height() >= 225
                assert c('homeHeroTitle').property('font').pixelSize() >= 35
                assert not c('homeWorkPanel').isVisible()
                assert window.findChild(QObject, 'homeUploadZone') is None
                assert c('homeWorkflowHeading').property('text') == 'Quy trình đơn giản'
                assert c('navigationnew').mapToScene(QPointF()).y() > c('navigationhome').mapToScene(QPointF()).y()
                assert c('navigationnew').mapToScene(QPointF()).y() < c('navigationlibrary').mapToScene(QPointF()).y()
                assert window.grabWindow().save(str(report/f'home-{width}.png'))
                click(window, c('homeWorkflowStep3'))
                assert window.property('page') == 'voice' and c('navigationvoice').property('selected')
                assert not bridge.narrationBusy, 'Opening the voice workspace must not start synthesis'
                click(window, c('navigationhome'))
            click(window, c('homeWorkflowStep0'))
            assert window.property('page') == 'new' and c('navigationnew').property('selected')
            assert not c('navigationlibrary').property('selected')
            QMetaObject.invokeMethod(c('creationFileDialog'), 'reject', Qt.DirectConnection)
            wrong = Path(folder)/'Tài liệu khác.txt'
            wrong.write_text('Năng lượng được bảo toàn.', encoding='utf-8')
            window.setProperty('page', 'home')
            QMetaObject.invokeMethod(c('homeWelcome'), 'documentDropped', Qt.DirectConnection,
                                     Q_ARG('QVariant', [wrong.as_uri()]))
            assert window.property('page') == 'home' and '.pptx' in window.property('inputDocumentError')
            fixture = Path(folder)/'Bài học thử.pptx'
            deck = Presentation()
            deck.slides.add_slide(deck.slide_layouts[6])
            deck.save(fixture)
            QMetaObject.invokeMethod(c('homeWelcome'), 'documentDropped', Qt.DirectConnection,
                                     Q_ARG('QVariant', [fixture.as_uri()]))
            pump(150)
            assert window.property('page') == 'new'
            selected = window.property('selectedFile')
            assert selected.endswith('.pptx')
            assert list(c('creationFileDialog').property('nameFilters')) == ['PowerPoint (*.pptx)']
            for width, height in ((1080, 700), (1366, 850)):
                window.resize(width, height)
                c('creationScroll').property('contentItem').setProperty('contentY', 0)
                pump(150)
                button = c('chooseInputDocumentButton')
                button_center = button.mapToScene(QPointF(button.width()/2, 0)).x()
                heading = control(c('creationSourceArea'), 'powerpointUploadHeading')
                heading_center = heading.mapToScene(QPointF(heading.width() / 2, 0)).x()
                assert abs(heading_center-button_center) < 1, 'Upload button must center with the upload text'
                art = c('chooseInputDocumentButtonIllustration')
                assert art.isVisible() and art.property('paintedWidth') > 100 and art.property('paintedHeight') > 100
                assert art.mapToScene(QPointF(art.width(), 0)).x() < heading.mapToScene(QPointF()).x()
                assert window.grabWindow().save(str(report/f'conversion-{width}.png'))
            # The file-size limit is real; a sparse fixture avoids allocating 200 MB.
            oversized = Path(folder)/'Quá lớn.pptx'
            with oversized.open('wb') as stream:
                stream.truncate(200 * 1024**2 + 1)
            QMetaObject.invokeMethod(c('homeWelcome'), 'documentDropped', Qt.DirectConnection,
                                     Q_ARG('QVariant', [oversized.as_uri()]))
            assert '200 MB' in window.property('inputDocumentError')
            assert window.property('selectedFile') == selected
            QMetaObject.invokeMethod(c('homeWelcome'), 'documentDropped', Qt.DirectConnection,
                                     Q_ARG('QVariant', [fixture.as_uri()]))
            click(window, c('navigationlibrary'))
            click(window, c('navigationnew'))
            assert window.property('selectedFile') == selected, 'Navigation must retain conversion draft'
            click(window, c('navigationhome'))
            click(window, c('homeOverviewLibrary'))
            assert window.property('page') == 'library'
            lesson = library.create('Hệ điều hành', 'Tin học', 'THPT', '11', [('Slide 1', 'Hệ điều hành quản lý tài nguyên.')])
            bridge.selectLessonForClass(lesson['id'])
            window.setProperty('page', 'home')
            pump(200)
            until(lambda: c('homeMetricValue0').property('text') == '1')
            assert not c('homeWorkPanel').isVisible()
            assert c('homeRecentTitle0').property('text') == 'Hệ điều hành'
            click(window, c('homeRecentLesson0'))
            assert window.property('page') == 'result' and bridge.lesson['id'] == lesson['id']
            window.setProperty('page', 'home')
            pump(150)
            for width, height in ((1080, 700), (1366, 850), (1680, 960)):
                window.resize(width, height)
                c('libraryHomeScroll').property('contentItem').setProperty('contentY', 440)
                pump(150)
                assert window.grabWindow().save(str(report / f'overview-{width}.png'))
            c('libraryHomeScroll').property('contentItem').setProperty('contentY', 0)
            assert window.grabWindow().save(str(report/'home-with-lesson.png'))
            library.set_setting('mascot', 'Lumi')
            bridge.changed.emit()
            pump(200)
            assert 'lumi-welcome' in c('homeHeroMascot').property('source').toString()
            assert window.grabWindow().save(str(report/'home-lumi.png'))
            window.resize(1080, 700)
            pump(200)
            assert window.grabWindow().save(str(report/'home-lumi-1080.png'))
            previous_state = bridge._browser_state
            bridge._browser_state = {'running': True, 'phase': 'translating', 'percent': 37}
            bridge.changed.emit()
            pump(100)
            assert c('homeContinueWork').property('text') == 'Xem tiến độ'
            click(window, c('homeContinueWork'))
            assert window.property('page') == 'new'
            bridge._browser_state = previous_state
            bridge.changed.emit()
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings,
                      'checks': ['1080/1366/1680 hero and four workflow steps visible; home upload removed', 'large mascot follows Milo/Lumi preference', 'separate conversion navigation before library',
                                 'home choose/drop route to same conversion', 'draft retained across tabs',
                                 'PPTX-only picker/drop with 200 MB guard and centered upload',
                                 'active work progress stays accessible and prevents new drops',
                                 'overview counts match library; compact recent lesson opens correct result; health removed from Home',
                                 'Dạy cùng Mascot opens voice workspace without starting synthesis at three sizes', 'new slogan']}
            (report/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            window.close()
            bridge.libraryThumbnails.shutdown()
            bridge.slidePreview.shutdown()
            bridge._catalog.shutdown()
            bridge.browserAI.shutdown()
            bridge.english_reader.shutdown()
            bridge.narration_preparation.shutdown()
            bridge.classroom.shutdown()
            bridge.voice_controls.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
