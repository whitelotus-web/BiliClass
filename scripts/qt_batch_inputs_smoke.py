"""Owned queue selection/preview race and layout checks; no teacher documents."""
import json
import sys
import tempfile
from pathlib import Path
from threading import Event
from unittest.mock import patch

from pptx import Presentation
from PySide6.QtCore import Q_ARG, QCoreApplication, QEvent, QMetaObject, QPointF, Qt, QUrl
from PySide6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QImage
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT/'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    report = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/batch-inputs')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-input-queue-', ignore_cleanup_errors=True) as temporary:
        folder = Path(temporary)
        sources, pictures = [], []
        for n, color in enumerate(('#c64b43', '#3776c5', '#309765')):
            deck = Presentation()
            for _ in range(n+2):
                deck.slides.add_slide(deck.slide_layouts[6])
            path = folder/f'Bài {n+1} có tên dài để thử hàng đợi, #1.pptx'
            deck.save(path)
            sources.append(path)
            picture = QImage(960, 540, QImage.Format_RGB32)
            picture.fill(QColor(color))
            image = folder/f'preview-{n}.png'
            assert picture.save(str(image))
            pictures.append(image.as_uri())
        original = [source.read_bytes() for source in sources]
        library = Library(folder/'data')
        library.set_setting('teaching_subjects', ['Toán'])
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        root.resize(1366, 850)
        root.show()
        entered, release = Event(), Event()
        delayed = [False]

        def renderer(url, directory, cancel, number=1):
            n = sources.index(Path(QUrl(url).toLocalFile()))
            if delayed[0] and n == 1:
                entered.set()
                assert release.wait(8)
                # Deliberately return a stale image despite cancellation.
            return dict(image=pictures[n], total=n+2, slide=number)

        def c(name):
            return control(root, name)

        def accept(method):
            assert QMetaObject.invokeMethod(root, method, Qt.DirectConnection,
                Q_ARG('QVariant', [path.as_uri() for path in sources]))

        inputs = bridge.batchQueue.inputs
        try:
            with patch('app.input_documents.input_preview', renderer):
                for kind, method, source_panel, config in (
                    ('convert', 'acceptInputDocuments', 'conversionBatchInputs', 'creationConfiguration'),
                    ('voice', 'acceptVoiceDocuments', 'voiceBatchInputs', 'lessonNarrationPanel'),
                ):
                    root.setProperty('page', 'new' if kind == 'convert' else 'voice')
                    accept(method)
                    until(lambda: len(inputs.details) == 3 and not inputs.documents.preview.get('busy', True))
                    ids = [row['id'] for row in bridge.batchQueue.data['rows']]
                    assert inputs.state['selected_id'] == ids[0]
                    assert inputs.documents.preview['image'] == pictures[0]
                    assert [row['total'] for row in inputs.state['rows']] == [2, 3, 4]
                    assert c(source_panel).isVisible()
                    assert c(source_panel).mapToScene(QPointF()).y() < c(config).mapToScene(QPointF()).y()
                    cancel = c('removeInputDocumentButton' if kind == 'convert' else 'dismissVoiceLesson')
                    assert cancel.isVisible() and cancel.isEnabled()
                    for theme in ('light', 'dark'):
                        bridge.setApplicationTheme(theme)
                        for width, height in ((1080, 700), (1366, 850)):
                            root.resize(width, height)
                            pump(100)
                            list_view, thumbnail = c('batchInputRows_'+kind), c('batchInputThumbnail_'+kind)
                            assert thumbnail.mapToScene(QPointF()).x() >= list_view.mapToScene(QPointF(list_view.width(), 0)).x()
                            assert abs(thumbnail.width()/thumbnail.height()-16/9) < .01
                            root.grabWindow().save(str(report/f'{kind}-{theme}-{width}.png'))
                    delayed[0] = True
                    entered.clear()
                    release.clear()
                    click(root, c('batchInputChoice_'+ids[1]))
                    until(entered.is_set)
                    click(root, c('batchInputChoice_'+ids[2]))
                    assert inputs.state['selected_id'] == ids[2]
                    release.set()
                    until(lambda: inputs.documents.preview.get('image') == pictures[2] and not inputs.documents.preview.get('busy'))
                    delayed[0] = False
                    click(root, c('batchInputNext_'+kind))
                    until(lambda: inputs.documents.preview.get('slide') == 2 and not inputs.documents.preview.get('busy'))
                    assert inputs.documents.preview['image'] == pictures[2]
                    click(root, c('batchInputPreviewToggle_'+kind))
                    assert c('batchInputExpanded_'+kind).isVisible()
                    click(root, c('batchInputPreviewToggle_'+kind))
                    opened = []
                    with patch.object(bridge, 'openInputPowerPoint', side_effect=opened.append):
                        click(root, c('batchInputOpen_'+ids[0]))
                    assert [Path(QUrl(url).toLocalFile()) for url in opened] == [sources[0]], opened
                    assert inputs.state['selected_id'] == ids[2], inputs.state
                    click(root, c('batchInputRemove_'+ids[2]))
                    until(lambda: inputs.state['selected_id'] == ids[0] and inputs.documents.preview.get('image') == pictures[0])
                    assert [row['id'] for row in bridge.batchQueue.data['rows']] == ids[:2]
                    click(root, cancel)
                    pump(100)
                    assert not bridge.batchQueue.data and not inputs.state['selected_id'] and not inputs.documents.preview
                    assert not bridge.busy and not bridge.narrationBusy
                assert library.db.execute('SELECT COUNT(*) FROM lessons').fetchone()[0] == 0
                assert [source.read_bytes() for source in sources] == original
                assert not warnings, warnings
            (report/'result.json').write_text(json.dumps(dict(status='passed', shared_convert_voice_input_panel=True,
                first_file_preview=True, latest_selection_wins=True, remove_selected_falls_back=True,
                per_file_open_keeps_selection=True, header_cancel_clears_only_inputs=True,
                slide_navigation_and_expand=True, metadata_real_pptx=True, sources_and_library_preserved=True,
                light_dark_1080_1366=True, qml_warnings=[])), encoding='utf-8')
            print('Batch input selection, preview race and layout Qt checks passed.', flush=True)
        finally:
            release.set()
            bridge.batchQueue.shutdown()
            for name in ('libraryThumbnails', 'googleSettings', '_library_preferences', 'slidePreview',
                         '_catalog', 'browserAI', 'english_reader', 'narration_preparation',
                         'narrationPreferences', '_companion_preferences', 'classroom', 'voice_controls', 'inputDocuments'):
                getattr(bridge, name).shutdown()
            c('companionWindow').setProperty('disposing', True)
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
