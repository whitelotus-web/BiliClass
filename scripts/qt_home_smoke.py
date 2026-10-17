"""Real Qt home/navigation flow, with a disposable library and no API calls."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, QObject, QPointF, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from pptx import Presentation
from qt_result_preview_mascot_smoke import click, control, pump

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc60/home')
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
            assert not c('homeTranslationUsage').isVisible()
            for width, height in ((1080, 700), (1366, 850), (1680, 960)):
                window.resize(width, height)
                c('libraryHomeScroll').property('contentItem').setProperty('contentY', 0)
                pump(250)
                for name in ('homeWelcomeHero', 'homeHeroMascot', 'homeChooseDocument', 'homeUploadZone'):
                    item = c(name)
                    point = item.mapToScene(QPointF())
                    assert point.x() >= 0 and point.x()+item.width() <= width, name
                    assert point.y() >= 0 and point.y()+item.height() < height, name
                assert c('homeHeroMascot').width() >= 185
                assert c('homeHeroMascot').height() >= 225
                assert c('homeHeroTitle').property('font').pixelSize() >= 35
                assert not c('homeWorkPanel').isVisible(), 'Empty library should lead with upload'
                assert c('navigationnew').mapToScene(QPointF()).y() > c('navigationhome').mapToScene(QPointF()).y()
                assert c('navigationnew').mapToScene(QPointF()).y() < c('navigationlibrary').mapToScene(QPointF()).y()
                assert window.grabWindow().save(str(report/f'home-{width}.png'))
            click(window, c('homeChooseDocument'))
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
                area, button = c('creationSourceArea'), c('chooseInputDocumentButton')
                area_center = area.mapToScene(QPointF(area.width()/2, 0)).x()
                button_center = button.mapToScene(QPointF(button.width()/2, 0)).x()
                assert abs(area_center-button_center) < 1, 'Upload button must be centered'
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
            click(window, c('homeHealthDetailsToggle'))
            assert c('homeTranslationUsage').isVisible()
            click(window, c('homeHealthDetailsToggle'))
            assert not c('homeTranslationUsage').isVisible()
            click(window, c('homeGoogleSettings'))
            assert window.property('page') == 'settings' and c('settingsPage').property('activeTab') == 6
            lesson = library.create('Hệ điều hành', 'Tin học', 'THPT', '11', [('Slide 1', 'Hệ điều hành quản lý tài nguyên.')])
            bridge.selectLessonForClass(lesson['id'])
            window.setProperty('page', 'home')
            pump(200)
            assert c('homeFeaturedTitle').property('text') == 'Hệ điều hành'
            assert c('homeContinueWork').property('text') == 'Mở bài giảng'
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
            assert c('homeChooseDocument').property('text') == 'Xem tiến độ'
            assert not c('homeUploadDrop').property('enabled')
            click(window, c('homeChooseDocument'))
            assert window.property('page') == 'new'
            bridge._browser_state = previous_state
            bridge.changed.emit()
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings,
                      'checks': ['1080/1366/1680 hero and upload visible without scrolling', 'large mascot follows Milo/Lumi preference', 'separate conversion navigation before library',
                                 'home choose/drop route to same conversion', 'draft retained across tabs',
                                 'PPTX-only picker/drop with 200 MB guard and centered upload',
                                 'active work progress stays accessible and prevents new drops',
                                 'collapsed health details and settings route', 'new slogan']}
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
