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
from qt_result_preview_mascot_smoke import click, control, pump

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc56/home')
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
            for width, height in ((1080, 700), (1366, 850)):
                window.resize(width, height)
                c('libraryHomeScroll').property('contentItem').setProperty('contentY', 0)
                pump(250)
                for name in ('homeWelcomeHero', 'homeContinueWork', 'homeWorkflow'):
                    item = c(name)
                    point = item.mapToScene(QPointF())
                    assert point.x() >= 0 and point.x()+item.width() <= width, name
                    assert point.y() >= 0 and point.y()+item.height() < height, name
                assert c('navigationnew').mapToScene(QPointF()).y() > c('navigationhome').mapToScene(QPointF()).y()
                assert c('navigationnew').mapToScene(QPointF()).y() < c('navigationlibrary').mapToScene(QPointF()).y()
                assert window.grabWindow().save(str(report/f'home-{width}.png'))
            click(window, c('homeContinueWork'))
            assert window.property('page') == 'new' and c('navigationnew').property('selected')
            assert not c('navigationlibrary').property('selected')
            QMetaObject.invokeMethod(c('creationFileDialog'), 'reject', Qt.DirectConnection)
            fixture = Path(folder)/'Bài học thử.txt'
            fixture.write_text('Năng lượng được bảo toàn.', encoding='utf-8')
            window.setProperty('page', 'home')
            QMetaObject.invokeMethod(c('homeWelcome'), 'documentDropped', Qt.DirectConnection,
                                     Q_ARG('QVariant', [fixture.as_uri()]))
            pump(150)
            assert window.property('page') == 'new'
            selected = window.property('selectedFile')
            assert selected.endswith('.txt')
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
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings,
                      'checks': ['1080/1366 layout', 'separate conversion navigation before library',
                                 'home choose/drop route to same conversion', 'draft retained across tabs',
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
