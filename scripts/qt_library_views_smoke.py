"""Real Qt list/cards, native first-slide covers and selection routing."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QPointF, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from qt_result_preview_mascot_smoke import click, control, pump, until
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc54/library-views'); report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-views-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        for title, subject, vi, en in [
            ('Dao động điều hòa', 'Vật lý', 'Vận tốc biến thiên tuần hoàn theo thời gian.', 'Velocity varies periodically with time.'),
            ('Hệ điều hành', 'Tin học', 'Hệ điều hành quản lý tài nguyên máy tính.', 'The operating system manages computer resources.'),
            ('Năng lượng trong cuộc sống', 'Vật lý', 'Năng lượng có thể chuyển từ dạng này sang dạng khác.', 'Energy can change from one form to another.')]:
            lesson = library.create(title, subject, 'THPT', '11', [('Slide 1', vi)])
            library.edit_segment(lesson['id'], lesson['segments'][0]['id'], vi, en, True)
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        c = lambda name: control(window, name)
        try:
            window.setProperty('page', 'library')
            until(lambda: len(bridge.lessons) == 3 and bridge._catalog.worker is None)
            pump(200)
            print('Catalog ready', flush=True)
            assert bridge.libraryView == 'list' and bridge.libraryThumbnails.worker is None
            identity = bridge.lessons[0]['id']
            click(window, c('lessonSelect_' + identity))
            click(window, c('libraryGridView'))
            print('Grid selected:', bridge.libraryView, window.property('libraryLarge'), flush=True)
            assert bridge.libraryView == 'grid'
            until(lambda: len(bridge.libraryCovers.images) == 3 and bridge.libraryThumbnails.worker is None, timeout=90)
            assert all(row['image'] for row in bridge.libraryCovers.images.values()), bridge.libraryCovers.images
            print('Native covers ready', flush=True)
            assert not bridge.lesson.get('id'), 'Covers must not select/open a lesson'
            assert library.setting('library_view', '') == 'grid'
            assert c('lessonSelect_' + identity).property('checked'), 'Switch must retain selection'
            click(window, c('lessonDownload_' + identity))
            assert c('libraryDownloadDialog').property('visible')
            ids = c('libraryDownloadDialog').property('identities').toVariant()
            assert ids == [identity]
            QMetaObject.invokeMethod(c('libraryDownloadDialog'), 'close', Qt.DirectConnection)
            for width, height, columns in ((1080, 700, 2), (1366, 850, 3)):
                window.resize(width, height); pump(250)
                c('libraryHomeScroll').property('contentItem').setProperty('contentY', 0); pump(100)
                assert c('libraryGrid').property('columns') == columns
                cover = c('lessonCover_' + identity)
                assert abs(cover.width()/cover.height() - 16/9) < .01
                sort = c('lessonSortOrder'); view = c('libraryGridView')
                pos = view.mapToScene(QPointF())
                assert pos.x() > sort.mapToScene(QPointF()).x() + sort.width()
                assert pos.x() + view.width() < width
                assert abs(pos.y() - sort.mapToScene(QPointF()).y()) < 3
                assert window.grabWindow().save(str(report / f'cards-{width}.png'))
            click(window, c('libraryListView')); pump(150)
            assert bridge.libraryView == 'list' and c('lessonSelect_' + identity).property('checked')
            assert window.grabWindow().save(str(report / 'list-1366.png'))
            with_read_only = Library.read_only(Path(folder))
            assert with_read_only.setting('library_view', '') == 'list'; with_read_only.close()
            click(window, c('libraryGridView')); pump(150)
            c('librarySearch').setProperty('text', 'tin hoc'); pump(400)
            assert len(bridge.libraryCovers.images) == 1
            assert not c('librarySelectAll').property('checked'), 'Filtering clears selection'
            window.setProperty('page', 'home'); pump(250)
            assert not c('libraryGrid').isVisible()
            assert not bridge.libraryCovers.images
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings, 'checks': [
                'native PowerPoint first-slide images for three disposable lessons',
                'no active lesson change from covers', 'list/grid preference persisted',
                'selection and exact download IDs survive switch', 'filters keep same behavior',
                '16:9 covers; 2 columns at 1080, 3 at 1366; controls right of sort', 'home stays list']}
            (report/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            window.close()
            bridge.libraryThumbnails.shutdown(); bridge.slidePreview.shutdown(); bridge._catalog.shutdown()
            bridge.browserAI.shutdown(); bridge.english_reader.shutdown(); bridge.narration_preparation.shutdown()
            bridge.classroom.shutdown(); bridge.voice_controls.shutdown()
            engine.deleteLater(); QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents(); library.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
