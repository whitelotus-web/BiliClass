"""Qt review routing and compact usage UI with isolated data.

The repair slot uses synthetic quality metadata to verify routing/approval
guards. This script is not evidence of native PowerPoint quality inspection.
"""

import json
import sys
import tempfile
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, Qt, QUrl, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import click, control, pump, until

from app.google_translation import KeyStore
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


class ReviewBridge(Bridge):
    repairs = 0
    inspections = 0

    @Slot(str)
    def openLesson(self, identity):
        item = self.library.get(identity)
        if item.get('external_deck'):
            self._show_lesson(item, {
                'lesson_id': identity, 'revision': item['revision'], 'external': True,
                'path': str(self.library.directory / 'fixture.pptx'), 'total': 2,
                'image': QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/book.svg')).toString(),
                'slide': 1, 'draft': True, 'warnings': [],
            })
        else:
            super().openLesson(identity)

    @Slot()
    def repairConvertedLesson(self):
        self.repairs += 1
        self._lesson['slide_quality']['counts']['FAIL'] = 0
        self.changed.emit()

    @Slot()
    def inspectSlideQuality(self):
        self.inspections += 1


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc69/review-usage')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-review-ui-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        pending = library.create('Bài chờ xác nhận', 'Vật lý', 'THPT', '11', [('Slide 1', 'Năng lượng được bảo toàn.')])
        pending = library.edit_segment(pending['id'], pending['segments'][0]['id'],
                                       pending['segments'][0]['vi'], 'Energy is conserved.', False)
        failed = library.create('Bài có lỗi kỹ thuật', 'Tin học', 'THPT', '11', [('Slide 1', 'Hệ điều hành quản lý tài nguyên.')])
        failed = library.edit_segment(failed['id'], failed['segments'][0]['id'],
                                      failed['segments'][0]['vi'], 'The operating system manages resources.', False)
        failed.update(external_deck={'total': 2}, slide_quality={
            'counts': {'FAIL': 2, 'CHECK': 0, 'PASS': 0}, 'local_repairs': [], 'slides': [],
        })
        library._write(failed)
        store = KeyStore(Path(folder))
        store.add('AIza' + 'a'*35 + '\nAIza' + 'b'*35)
        store.reserve(40000, 500000)
        with closing(store.connect()) as ledger, ledger:
            ledger.execute('UPDATE usage SET characters=characters+104853')
            ledger.execute('UPDATE usage_per_key SET carryover=104853')
        bridge = ReviewBridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]

        def c(name):
            return control(window, name)

        try:
            window.setProperty('page', 'library')
            until(lambda: len(bridge.lessons) == 2 and bridge._catalog.worker is None)
            pump(150)
            assert c('lessonStatus_' + pending['id']).property('text') == 'Chờ xác nhận'
            assert c('lessonStatus_' + failed['id']).property('text') == '2 slide cần sửa'
            click(window, c('lessonStatus_' + pending['id']))
            until(lambda: c('lessonReviewHelpDialog').property('visible'))
            assert not c('reviewConfirmLesson').isEnabled(), 'Create/view presentation before teaching'
            assert c('reviewBuildPreview').isVisible()
            assert not any(s['approved'] for s in library.get(pending['id'])['segments'])
            QMetaObject.invokeMethod(c('lessonReviewHelpDialog'), 'close', Qt.DirectConnection)
            window.setProperty('page', 'library')
            pump(100)
            click(window, c('lessonStatus_' + failed['id']))
            until(lambda: c('lessonReviewHelpDialog').property('visible'))
            assert not c('reviewConfirmLesson').isEnabled()
            assert c('reviewRepairSlides').isVisible()
            assert window.grabWindow().save(str(report / 'repair-dialog.png'))
            click(window, c('reviewInspectSlides'))
            assert bridge.inspections == 1
            click(window, c('reviewRepairSlides'))
            assert bridge.repairs == 1 and bridge.lessonReview['kind'] == 'confirm'
            assert not any(s['approved'] for s in bridge.lesson['segments'])
            click(window, c('reviewConfirmLesson'))
            assert c('wholeLessonReview').property('visible')
            assert not any(s['approved'] for s in library.get(failed['id'])['segments'])
            QMetaObject.invokeMethod(c('wholeLessonReview'), 'close', Qt.DirectConnection)
            window.setProperty('page', 'settings')
            descriptions = set()
            for tab in (0, 6, 2, 3, 4, 5, 1):
                c('settingsPage').setProperty('activeTab', tab)
                pump(50)
                assert c('settingsPageTitle').property('text') == 'Cài đặt'
                descriptions.add(c('settingsPageDescription').property('text'))
            assert len(descriptions) == 7
            c('settingsPage').setProperty('activeTab', 6)
            pump(150)
            rows = bridge.googleSettings.state['keys']
            assert rows[0]['used'] == 40000 and rows[1]['used'] == 0
            assert '355.147 / 500.000' in c('googleKeyRemaining_' + rows[0]['id']).property('text')
            assert '500.000 / 500.000' in c('googleKeyRemaining_' + rows[1]['id']).property('text')
            assert not c('googleApiKeys').isVisible()
            for removed in ('googleCharacterBudget', 'toggleGoogleAdvanced', 'settingsTranslationUsage',
                            'receiveGoogleKeysGitHub', 'sendGoogleKeysGitHub', 'preparePictureOcr'):
                assert window.findChild(QObject, removed) is None, removed
            for width, height in ((1080, 700), (1366, 850)):
                window.resize(width, height)
                pump(150)
                assert window.grabWindow().save(str(report / f'google-{width}.png'))
            click(window, c('toggleGoogleKeyEntry'))
            assert c('googleApiKeys').isVisible()
            click(window, c('toggleGoogleKeyEntry'))
            assert store.public()[0]['used'] == 40000
            assert store.public()[0]['project'] == 'mặc định'
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings, 'checks': [
                'status badge explains and routes without selecting a card',
                'technical failures block confirmation; repair/inspect route to existing slots',
                'repair does not approve text; confirmation opens explicit teacher review',
                'two unlabelled keys have separate counters and remaining/total beneath each key',
                'local key entry and per-key counters; removed sync/advanced controls; usage preserved',
                '1080/1366 screenshots',
            ]}
            (report / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
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
