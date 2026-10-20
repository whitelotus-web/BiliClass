"""Theme, compact preview, task return and 60px companion in isolated Qt windows."""
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageDraw
from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, QPointF, Qt, QUrl, Slot
from PySide6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QImage
from PySide6.QtQml import QQmlApplicationEngine, QQmlEngine, QQmlExpression
from PySide6.QtQuickControls2 import QQuickStyle

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump, until


class PreviewFixtureBridge(Bridge):
    """Only the Office renderer is replaced; the workspace and signals are real."""
    preview_calls = 0

    @Slot(int)
    def previewConvertedSlide(self, slide):
        self.preview_calls += 1
        self._quick_result.update(slide=slide, image=self.fixture_image)
        self.quickResultChanged.emit()


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle('Basic')
    for font in (RESOURCE_ROOT/'assets').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont('Be Vietnam Pro', 10))
    reports = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/application-theme')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-theme-', ignore_cleanup_errors=True) as folder:
        folder = Path(folder)
        library = Library(folder/'data')
        lesson = library.create('Bài thử giao diện', 'Vật lý', 'THPT', '10', [('Năng lượng.', 'Energy.')])
        image = QImage(1600, 900, QImage.Format_RGB32)
        image.fill(QColor('#ffffff'))
        image.save(str(folder/'slide.png'))
        bridge = PreviewFixtureBridge(library)
        bridge.fixture_image = QUrl.fromLocalFile(str(folder/'slide.png')).toString()
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        root.resize(1366, 850)

        def c(name):
            return control(root, name)

        def invoke(obj, method):
            assert QMetaObject.invokeMethod(obj, method, Qt.DirectConnection)
            pump(80)

        def evaluate(obj, expression):
            value, error = QQmlExpression(QQmlEngine.contextForObject(obj), obj, expression).evaluate()
            assert not error, expression
            return value

        try:
            for mode in ('dark', 'light', 'dark'):
                bridge.setApplicationTheme(mode)
                pump(80)
                assert root.color().name() == ('#101827' if mode == 'dark' else '#f3f7fc')
                for page in ('home', 'new', 'library', 'voice', 'settings'):
                    root.setProperty('page', page)
                    pump(60)
                    assert root.grabWindow().save(str(reports/f'{mode}-{page}.png'))
                for index in (0, 1, 2, 3, 5, 6):
                    c('settingsPage').setProperty('activeTab', index)
                    pump(60)
                    root.grabWindow().save(str(reports/f'{mode}-settings-{index}.png'))
            c('settingsPage').setProperty('activeTab', 0)
            pump(100)
            scroll = c('settingsContentScroll').property('contentItem')
            scroll.setProperty('contentY', max(0, scroll.property('contentHeight')-scroll.height()))
            pump(100)
            assert c('applicationThemeLight').isVisible() and c('applicationThemeDark').property('checked')
            root.grabWindow().save(str(reports/'appearance-picker.png'))
            invoke(c('helpDialog'), 'open')
            assert evaluate(c('helpDialog'), 'palette.window.toString()') == '#101827'
            assert evaluate(c('helpDialog'), 'background.color.toString()') == '#182438'
            root.grabWindow().save(str(reports/'dark-help.png'))
            invoke(c('helpDialog'), 'close')
            # A converted lesson has a 16:9 thumbnail before any preview click.
            bridge._lesson = lesson
            bridge._quick_result = dict(lesson_id=lesson['id'], revision=lesson['revision'], path='fixture.pptx', total=2, slide=1)
            bridge.changed.emit()
            bridge.quickResultChanged.emit()
            root.setProperty('page', 'voice')
            until(lambda: bool(bridge.quickResult.get('image')))
            assert bridge.preview_calls == 1
            thumbnail = c('voiceSlideThumbnail')
            assert thumbnail.isVisible() and abs(thumbnail.width()/thumbnail.height()-16/9) < .01
            c('toggleVoiceSlidePreview').clicked.emit()
            pump(100)
            assert root.property('voicePreviewExpanded') and not thumbnail.isVisible()
            c('toggleVoiceSlidePreview').clicked.emit()
            pump(100)
            assert thumbnail.isVisible() and bridge.preview_calls == 1
            root.grabWindow().save(str(reports/'dark-voice-thumbnail.png'))
            # Generic tasks return to their originating Settings subtab.
            root.setProperty('page', 'settings')
            c('settingsPage').setProperty('activeTab', 2)
            bridge._busy = True
            bridge.changed.emit()
            pump(70)
            status = c('applicationStatusMessage')
            assert not status.property('returnable')
            root.setProperty('page', 'library')
            pump(70)
            assert status.property('returnable') and status.isEnabled()
            root.setProperty('dirty', True)
            status.clicked.emit()
            pump(80)
            assert root.property('page') == 'library' and c('unsavedDialog').property('visible')
            invoke(c('unsavedDialog'), 'close')
            root.setProperty('dirty', False)
            status.clicked.emit()
            pump(80)
            assert root.property('page') == 'settings' and c('settingsPage').property('activeTab') == 2
            assert not status.property('returnable')
            bridge._busy = False
            bridge.changed.emit()
            pump(60)
            assert not status.isEnabled()
            # Narration and conversion jobs have their own stable workspace.
            bridge.narration_preparation.worker = object()
            bridge.narration_preparation.state = dict(lesson_id=lesson['id'], mode='both',
                                                     running=True, complete=1, total=2, percent=50)
            bridge.narrationChanged.emit()
            root.setProperty('page', 'library')
            pump(60)
            assert status.property('returnable') and '50%' in status.property('text')
            status.clicked.emit()
            pump(60)
            assert root.property('page') == 'voice' and not status.property('returnable')
            bridge.narration_preparation.worker = None
            bridge.narration_preparation.state = {}
            bridge.narrationChanged.emit()
            bridge._browser_state.update(running=True, phase='translate', percent=30)
            bridge.browserStateChanged.emit()
            root.setProperty('page', 'library')
            pump(60)
            assert status.property('returnable')
            status.clicked.emit()
            pump(60)
            assert root.property('page') == 'chatgpt' and not status.property('returnable')
            bridge._browser_state['running'] = False
            bridge.browserStateChanged.emit()
            # Update downloads are a distinct task, with an explicit destination.
            bridge._update_state.update(downloading=True, message='Đang tải bản cập nhật…')
            bridge.updateChanged.emit()
            root.setProperty('page', 'home')
            pump(60)
            assert status.property('returnable')
            status.clicked.emit()
            pump(60)
            assert root.property('page') == 'settings' and c('settingsPage').property('activeTab') == 1
            bridge._update_state['downloading'] = False
            bridge.updateChanged.emit()
            # Mascot follows the same theme, and 60px has a smaller panel than 80px.
            companion = c('companionWindow')
            bridge.teaching_session.bound = {'lesson': {**lesson, 'narration': {'keys': {'vi': ['fixture']}}}}
            bridge.powerpoint_worker = SimpleNamespace(navigate=lambda *_: None)
            bridge._powerpoint_state.update(active=True, opened=True, slide=1, total=2)
            bridge.powerpointStateChanged.emit()
            dimensions = {}
            for pixels in (60, 65, 66, 80, 94, 95, 110, 129, 130, 150, 160):
                bridge.saveMascotPreferences('Milo', True, pixels, 'right', False, True, True, True)
                until(lambda: not bridge.mascotSaving)
                bridge.showCompanion(companion)
                companion.setProperty('collapsed', False)
                pump(120)
                dimensions[pixels] = (companion.width(), c('companionMenu').height())
                companion.grabWindow().save(str(reports/f'dark-mascot-{pixels}.png'))
                assert c('companionSettings').mapToScene(QPointF()).x() > 0
                options = c('companionReadingOptions')
                assert options.isVisible()
                first, last = c('companionReadingAuto'), c('companionReadingFull')
                middle = (first.mapToScene(QPointF()).x() + last.mapToScene(QPointF(last.width(), 0)).x())/2
                assert abs(middle-options.mapToScene(QPointF(options.width()/2, 0)).x()) < 1
                assert 'Bấm loa để nghe lại' not in c('companionAudioHint').property('text')
                start = c('companionStartShow')
                label = start.findChild(QObject, 'actionButtonLabel')
                assert start.property('text') == 'Đang chiếu'
                assert label.property('contentWidth') <= label.width()+1
            assert dimensions[60][0] == 280 < dimensions[80][0], dimensions
            assert dimensions[60][1] < dimensions[80][1]
            invoke(c('companionPresentationDialog'), 'open')
            pump(120)
            assert c('companionPresentationDialog').property('visible')
            root.grabWindow().save(str(reports/'dark-file-picker.png'))
            invoke(c('companionPresentationDialog'), 'close')
            root.setProperty('page', 'settings')
            c('settingsPage').setProperty('activeTab', 0)
            # Round logos lose only empty white corners; square/wide marks keep
            # all their pixels. The saved source is never rewritten by display.
            logo = Image.new('RGBA', (256, 256), 'white')
            draw = ImageDraw.Draw(logo)
            draw.ellipse((1, 1, 254, 254), outline='#1377bc', width=10)
            draw.ellipse((70, 70, 185, 185), fill='#1377bc')
            assets = library.directory/'assets'
            assets.mkdir(exist_ok=True)
            path = assets/'school-logo.png'
            logo.save(path)
            before = path.read_bytes()
            bridge._logo_revision += 1
            bridge.changed.emit()
            until(lambda: evaluate(c('sidebarSchoolLogo'), 'Number(status)') == 1)
            pump(160)
            assert bridge.schoolLogoRound and c('sidebarSchoolLogo').property('roundMask')
            sidebar = c('sidebarSchoolLogo')
            point = sidebar.mapToScene(QPointF(1, 1))*root.devicePixelRatio()
            assert root.grabWindow().pixelColor(round(point.x()), round(point.y())).name() != '#ffffff'
            root.grabWindow().save(str(reports/'round-school-logo.png'))
            assert before == path.read_bytes()
            draw.rectangle((0, 0, 25, 25), fill='red')
            logo.save(path)
            bridge._logo_revision += 1
            bridge.changed.emit()
            pump(150)
            assert not bridge.schoolLogoRound and not sidebar.property('roundMask')
            assert library.setting('application_theme', '') == 'dark'
            assert len(library.list_lessons(verify_audio=False)) == 1
            assert not warnings, warnings
            result = dict(status='passed', warnings=warnings, dimensions=dimensions,
                          checks=['light/dark across pages and Settings tabs', 'dialogs inherit dark palette',
                                  '16:9 thumbnail expands/collapses without repeated render',
                                  'task return preserves Settings subtab and dirty guard',
                                  'update task destination', '60px companion shrinks further'])
            (reports/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
        finally:
            bridge._busy = False
            bridge.narration_preparation.worker = None
            bridge.powerpoint_worker = None
            bridge.teaching_session.bound = {}
            for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                           bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                           bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                worker.shutdown()
            c('companionWindow').setProperty('disposing', True)
            c('companionWindow').hide()
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
