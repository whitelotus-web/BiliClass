"""Exercise the restored upload panel and reachable conversion controls in Qt."""

import json
import logging
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pptx import Presentation
from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import click, control, pump

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    out = Path("reports/rc70/conversion")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bcl-compact-conversion-", ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        library = Library(temp / "data")
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(RESOURCE_ROOT / "qml/Main.qml")
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]

        def c(name):
            return control(window, name)

        measurements = []
        def verify_layout(entry, scroll):
            upload = c('creationSourceArea')
            assert upload.property('compact') and not upload.property('condensed')
            assert upload.height() >= 140, 'Keep the illustrated upload panel readable'
            icon = c('chooseInputDocumentButtonIllustration')
            button = c('chooseInputDocumentButton')
            assert icon.width() >= 139 and icon.height() >= 109
            assert button.mapToScene(QPointF(0, 0)).x() > icon.mapToScene(QPointF(icon.width(), 0)).x()
            entry['requires_scroll'] = entry['content'] > entry['viewport'] + 1
            if entry['requires_scroll']:
                assert entry['height'] < 980, entry
                # The restored panel retains its original size. Extra fields
                # must remain reachable when a short window needs scrolling.
                flick = scroll.property('contentItem')
                flick.setProperty('contentY', entry['content'] - entry['viewport'])
                pump(80)
            else:
                assert not c('creationScrollBar').isVisible(), entry
            bottom = c('creationConfiguration').mapToScene(QPointF(0, c('creationConfiguration').height())).y()
            viewport_bottom = scroll.mapToScene(QPointF(0, scroll.property('availableHeight'))).y()
            assert bottom <= viewport_bottom + 1, entry
            summary = c('conversionConfigurationSummary')
            assert summary.isVisible()
            assert summary.mapToScene(QPointF(0, summary.height())).y() <= viewport_bottom + 1, entry
        try:
            window.setProperty("page", "new")
            path = temp / "Bài giảng PowerPoint có tên dài để kiểm tra bố cục.pptx"
            deck = Presentation()
            deck.slides.add_slide(deck.slide_layouts[6])
            deck.save(path)
            for width, height in ((1080, 700), (1366, 768), (1366, 850), (1920, 1080)):
                window.resize(width, height)
                pump(200)
                for selected in (False, True):
                    if selected:
                        QMetaObject.invokeMethod(
                            window,
                            "acceptInputDocuments",
                            Qt.DirectConnection,
                            Q_ARG("QVariant", [path.as_uri()]),
                        )
                        c("lessonSubject").setProperty(
                            "currentIndex", bridge.conversionSubjects.index("Tin học")
                        )
                    else:
                        QMetaObject.invokeMethod(window, "removeInputDocument", Qt.DirectConnection)
                    for template in (False, True):
                        click(window, c("creationUseTemplate" if template else "creationKeepOriginal"))
                        pump(130)
                        scroll = c("creationScroll")
                        flick = scroll.property("contentItem")
                        flick.setProperty("contentY", 0)
                        pump(50)
                        entry = {
                            "width": width,
                            "height": height,
                            "selected": selected,
                            "template": template,
                            "content": scroll.property("contentHeight"),
                            "viewport": scroll.property("availableHeight"),
                            "upload": c("creationSourceArea").height(),
                            "config": c("creationConfiguration").height(),
                        }
                        verify_layout(entry, scroll)
                        flick.setProperty('contentY', 0)
                        pump(50)
                        measurements.append(entry)
                        window.grabWindow().save(
                            str(out / f"{width}-{height}-{int(selected)}-{int(template)}.png")
                        )
                        c('lessonSubject').setProperty('currentIndex', bridge.conversionSubjects.index('Khác'))
                        c('creationCustomSubject').setProperty('text', 'Môn học riêng')
                        pump(150)
                        custom = {**entry, 'other_subject': True,
                                  'content': scroll.property('contentHeight'), 'viewport': scroll.property('availableHeight')}
                        verify_layout(custom, scroll)
                        measurements.append(custom)
                        c('lessonSubject').setProperty('currentIndex', bridge.conversionSubjects.index('Tin học'))
                        pump(50)
                QMetaObject.invokeMethod(window, 'removeInputDocument', Qt.DirectConnection)
                window.setProperty('page', 'new')
                pump(150)
                creation_height = c('creationSourceArea').height()
                window.setProperty('page', 'voice')
                pump(150)
                voice = c('voiceSourceArea')
                assert abs(voice.height() - creation_height) <= 1, (voice.height(), creation_height)
                assert voice.property('compact') and not voice.property('condensed')
                window.grabWindow().save(str(out / f'voice-{width}-{height}.png'))
                window.setProperty('page', 'new')
            assert not warnings, warnings
            result = {"status": "passed", "measurements": measurements, "qml_warnings": warnings}
            (out / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps(result), flush=True)
        finally:
            window.hide()
            for worker in (
                bridge.libraryThumbnails,
                bridge.slidePreview,
                bridge._catalog,
                bridge.browserAI,
                bridge.english_reader,
                bridge.narration_preparation,
                bridge.classroom,
                bridge.voice_controls,
            ):
                worker.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
            logging.shutdown()


if __name__ == "__main__":
    main()
