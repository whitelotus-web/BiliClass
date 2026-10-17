"""Measure and exercise conversion at short desktop sizes without API requests."""

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
    out = Path("reports/rc69/conversion")
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
                        assert entry['content'] <= entry['viewport'] + 1, entry
                        assert not c('creationScrollBar').isVisible(), entry
                        bottom = c('creationConfiguration').mapToScene(QPointF(0, c('creationConfiguration').height())).y()
                        viewport_bottom = scroll.mapToScene(QPointF(0, scroll.property('availableHeight'))).y()
                        assert bottom <= viewport_bottom + 1, entry
                        measurements.append(entry)
                        window.grabWindow().save(
                            str(out / f"{width}-{height}-{int(selected)}-{int(template)}.png")
                        )
                        c('lessonSubject').setProperty('currentIndex', bridge.conversionSubjects.index('Khác'))
                        c('creationCustomSubject').setProperty('text', 'Môn học riêng')
                        pump(150)
                        custom = {**entry, 'other_subject': True,
                                  'content': scroll.property('contentHeight'), 'viewport': scroll.property('availableHeight')}
                        assert custom['content'] <= custom['viewport'] + 1, custom
                        measurements.append(custom)
                        c('lessonSubject').setProperty('currentIndex', bridge.conversionSubjects.index('Tin học'))
                        pump(50)
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
