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
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


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
        lesson = library.create('Bài 6 – Dao động tắt dần, dao động cưỡng bức và hiện tượng cộng hưởng',
                                'Vật lý', 'THPT', '11', [('Năng lượng.', 'Energy.')])
        lesson = library.edit_segment(lesson['id'], lesson['segments'][0]['id'], 'Năng lượng.', 'Energy.', True)
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

        def centered(summary, keys):
            rows = {}
            for key in keys:
                badge = c(summary.objectName()+'_'+key)
                point = badge.mapToItem(summary, QPointF())
                rows.setdefault(round(point.y()), []).append((point.x(), point.x()+badge.width()))
            for row in rows.values():
                assert abs(min(left for left, _ in row)+max(right for _, right in row)-summary.width()) < 2

        language_layouts = []

        def separated_language_groups(width, selected):
            row = c('narrationLanguagePositionRow')
            panel = c('lessonNarrationPanel')
            language_cell, position_cell = c('narrationLanguageCell'), c('narrationPositionCell')
            languages, position = c('narrationLanguageChoices'), c('narrationPositionControls')
            assert abs(row.width()-evaluate(row, 'parent.width')) < 2
            assert abs(language_cell.width()-position_cell.width()) < 2
            for content, cell in ((languages, language_cell), (position, position_cell)):
                center = content.mapToItem(cell, QPointF(content.width()/2, content.height()/2))
                assert abs(center.x()-cell.width()/2) < 1
                assert abs(center.y()-cell.height()/2) < 1
                assert content.width() <= cell.width()+1
            columns = row.property('columns')
            assert columns == (2 if width >= 1366 else 1)
            if columns == 2:
                assert position_cell.x() >= language_cell.x()+language_cell.width()+23
                assert abs(languages.mapToItem(row, QPointF(0,languages.height()/2)).y()
                           -position.mapToItem(row, QPointF(0,position.height()/2)).y()) < 1
            else:
                assert position_cell.y() >= language_cell.y()+language_cell.height()+9
            buttons = [c(name) for name in ('narrationEnglish','narrationVietnamese','narrationBoth')]
            for button in buttons:
                point = button.mapToItem(languages,QPointF())
                assert point.x() >= 0 and point.x()+button.width() <= languages.width()+1
                detail = c(button.objectName()+'Detail')
                card = c(button.objectName()+'Card')
                assert detail.isVisible() and detail.property('text') and not detail.property('truncated')
                assert detail.property('contentHeight') <= detail.height()+1
                assert detail.mapToItem(card,QPointF(0,detail.height())).y() <= card.height()-11
                assert button.mapToItem(card,QPointF(0,button.height())).y()+4 <= detail.mapToItem(card,QPointF()).y()
            assert c('narrationPositionDescription').isVisible()
            title = c('narrationConfigurationTitle')
            assert title.mapToItem(panel,QPointF()).y() >= 16
            assert row.mapToItem(panel,QPointF(0,row.height())).y() <= panel.height()-15
            voice_choice = c('lessonNarrationVoiceChoice')
            assert row.mapToItem(panel,QPointF()).y() >= voice_choice.mapToItem(panel,QPointF(0,voice_choice.height())).y()+11
            if not selected:
                picker = c('selectVoiceLibraryLesson')
                gap = panel.mapToScene(QPointF()).y()-picker.mapToScene(QPointF(0,picker.height())).y()
                assert 30 <= gap <= 70, gap
                assert panel.height() >= 195, panel.height()
            language_layouts.append(dict(width=width, selected=selected, columns=columns,
                                         cell_width=language_cell.width(), row_width=row.width(), panel_height=panel.height()))

        try:
            for mode in ('dark', 'light', 'dark'):
                bridge.setApplicationTheme(mode)
                pump(80)
                assert root.color().name() == ('#101827' if mode == 'dark' else '#f3f7fc')
                for page in ('home', 'new', 'library', 'voice', 'settings'):
                    root.setProperty('page', page)
                    pump(60)
                    assert root.grabWindow().save(str(reports/f'{mode}-{page}.png'))
                    if page == 'voice':
                        for width, height in ((1080,700),(1366,850),(1920,1080)):
                            root.resize(width,height); pump(100)
                            separated_language_groups(width, False)
                            root.grabWindow().save(str(reports/f'{mode}-empty-voice-{width}.png'))
                        root.resize(1366,850); pump(80)
                for index in (0, 1, 2, 3, 5, 6):
                    c('settingsPage').setProperty('activeTab', index)
                    pump(60)
                    root.grabWindow().save(str(reports/f'{mode}-settings-{index}.png'))
            root.setProperty('page', 'library')
            until(lambda: bridge._catalog.worker is None)
            pump(100)
            status = c('lessonStatus_' + lesson['id'])
            original_row = next(row for row in bridge.lessons if row['id'] == lesson['id'])
            seen_fills = {}
            for audio, label in [
                ({'status': 'none'}, 'Chưa có giọng'),
                ({'status': 'none', 'variants': [{'status': 'partial', 'ready': False}]}, 'Chưa có giọng'),
                ({'status': 'stale', 'variants': [{'mode': 'en', 'ready': True}]}, 'Có giọng Anh'),
                ({'status': 'ready', 'variants': [{'mode': 'en', 'ready': True}, {'mode': 'vi', 'ready': True}]}, 'Có giọng Việt + Anh'),
                ({'status': 'unknown'}, 'Chưa có giọng'),
                ({'status': 'checking'}, 'Đang kiểm tra giọng…'),
            ]:
                for mode in ('light', 'dark'):
                    bridge.setApplicationTheme(mode)
                    status.setProperty('lessonRow', {**original_row, 'narration': audio})
                    pump(40)
                    assert status.property('text') == label
                    text = status.findChild(QObject, 'libraryVoicePillText')
                    assert not text.property('truncated'), (label, text.width(), text.property('contentWidth'))
                    fill = evaluate(status, 'background.color.toString()')
                    ink = text.property('color').name()
                    assert fill != ink
                    seen_fills.setdefault(mode, {})[label] = fill
            for fills in seen_fills.values():
                assert len({fills[label] for label in ('Chưa có giọng', 'Có giọng Anh', 'Đang kiểm tra giọng…')}) == 3
            status.setProperty('lessonRow', original_row)
            root.grabWindow().save(str(reports/'clear-library-status.png'))
            root.setProperty('page', 'settings')
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
            root.setProperty('page', 'new')
            c('creationUseTemplate').clicked.emit()
            pump(80)
            powerpoint_before = dict(bridge.powerpointState)
            for preset in ('standard', 'visual', 'practice'):
                c('creationPresetView_'+preset).clicked.emit()
                until(lambda: c('creationTemplateImageDialog').property('visible'))
                until(lambda: evaluate(c('creationTemplateImage'), 'Number(status)') == 1)
                assert c('creationTemplateImage').property('source').toString().endswith('/'+preset+'.png')
                assert bridge.powerpointState == powerpoint_before
                root.grabWindow().save(str(reports/f'template-image-{preset}.png'))
                invoke(c('creationTemplateImageDialog'), 'close')
            for name in ('formatChoice_parallel_columnsCard', 'formatChoice_english_onlyCard',
                         'creationKeepOriginalCard', 'creationUseTemplateCard'):
                assert evaluate(c(name), 'border.width') == 1 and evaluate(c(name), 'border.color.a') > 0
            conversion_summary = c('conversionConfigurationSummary')
            for choice in bridge.conversionFormats:
                c('formatChoice_'+choice['id']).clicked.emit()
                pump(50)
                assert evaluate(conversion_summary, 'entries[0].text') == choice['label']
            for index, preset in enumerate(('standard', 'visual', 'practice')):
                c('creationPresetSelect_'+preset).clicked.emit()
                pump(50)
                assert c('creationPreset').property('currentIndex') == index
                assert evaluate(conversion_summary, 'entries[1].text').startswith('Mẫu: ')
                assert c('creationPreset').property('currentText') in evaluate(conversion_summary, 'entries[1].text')
                centered(conversion_summary, ('language', 'design', 'subject', 'class'))
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
            for width, height in ((1080, 700), (1366, 850), (1920, 1080)):
                root.resize(width, height)
                pump(150)
                assert c('voiceWorkflowGuide').property('lineCount') == 1
                overview, details = c('voiceLessonOverview'), c('voiceLessonDetails')
                assert overview.property('columns') == 2
                assert thumbnail.mapToScene(QPointF()).x() >= details.mapToScene(QPointF()).x()+details.width()+23
                button = c('voiceTeachWithoutNarration')
                assert button.isVisible()
                assert button.mapToScene(QPointF()).y() < thumbnail.mapToScene(QPointF()).y()+thumbnail.height()+80
                assert overview.height() < 290
                assert abs(thumbnail.width()/thumbnail.height()-16/9) < .01
                summary, footer, create = c('narrationConfiguration'), c('creationFooter'), c('createLessonNarrationButton')
                assert c('narrationConfigurationTitle').property('text') == 'Cấu hình tạo giọng đọc'
                language_row, panel = c('narrationLanguagePositionRow'), c('lessonNarrationPanel')
                assert abs(language_row.mapToItem(panel, QPointF(language_row.width()/2, 0)).x()-panel.width()/2) < 2
                separated_language_groups(width, True)
                assert summary.isVisible()
                centered(summary, ('language', 'voice', 'rate', 'speakers', 'coverage'))
                point = summary.mapToItem(footer, QPointF())
                assert abs(point.x()-28) <= 1 and point.y() >= 12
                assert point.y()+summary.height() <= footer.height()-11
                assert summary.mapToScene(QPointF(summary.width(), 0)).x()+15 <= create.mapToScene(QPointF()).x()
                for key in ('language', 'voice', 'rate', 'speakers', 'coverage'):
                    badge = c('narrationConfiguration_'+key)
                    origin = badge.mapToItem(summary, QPointF())
                    assert origin.x() >= 10 and origin.y() >= 10
                    assert origin.x()+badge.width() <= summary.width()-9
                    assert origin.y()+badge.height() <= summary.height()-9
                fixed_y = summary.mapToScene(QPointF()).y()
                scroll = c('resultScroll').property('contentItem')
                scroll.setProperty('contentY', max(0, scroll.property('contentHeight')-scroll.height()))
                pump(60)
                assert abs(summary.mapToScene(QPointF()).y()-fixed_y) < 1
                scroll.setProperty('contentY', 0)
                pump(60)
                root.grabWindow().save(str(reports/f'compact-voice-overview-{width}.png'))
            root.resize(1366, 850)
            pump(100)
            # Real language/position controls update only the display overlay;
            # selecting a position persists it without re-rendering the slide.
            preview = c('thumbnailSpeakerPreview')
            until(lambda: preview.isVisible())
            for mode, button_name in (('en', 'narrationEnglish'), ('vi', 'narrationVietnamese'), ('both', 'narrationBoth')):
                c(button_name).clicked.emit()
                pump(80)
                assert root.property('narrationMode') == mode
                assert c('narrationConfiguration').property('mode') == mode
                names = bridge.voicePairDetails(root.property('narrationVoice'))['label'].split(' – ')
                assert c('narrationConfiguration').property('selectedVoice') == (
                    ' + '.join(names) if mode == 'both' else names[mode == 'en'])
                expected = ['vi', 'en'] if mode == 'both' else [mode]
                assert evaluate(preview, 'languages.join(",")') == ','.join(expected)
                for index, position in enumerate(('top_left', 'top_center', 'top_right', 'bottom_left', 'bottom_center', 'bottom_right')):
                    choice = c('narrationSpeakerPosition')
                    click(root, choice)
                    click(root, c('speakerPosition_'+position))
                    assert not bridge.busy, 'A speaker position must not trigger global loading'
                    until(lambda: not bridge.busy)
                    until(lambda: preview.property('position') == position)
                    assert c('narrationConfiguration').property('positionLabel') == choice.property('currentText')
                    assert choice.property('currentText') in evaluate(c('narrationConfiguration'), 'entries[3].text')
                    group = c('thumbnailSpeakerPreviewGroup')
                    assert group.y() >= 0 and group.y()+group.height() <= preview.height()
                    assert group.x() >= 0 and group.x()+group.width() <= preview.width()
                    if index < 3:
                        assert group.y() < preview.height()/2
                    else:
                        assert group.y() > preview.height()/2
                    if index % 3 == 0:
                        assert group.x() < preview.width()/4
                    elif index % 3 == 1:
                        assert abs(group.x()+group.width()/2-preview.width()/2) < 1
                    else:
                        assert group.x() > preview.width()/2
                    for language in expected:
                        until(lambda: evaluate(c('thumbnailSpeakerPreview_'+language), 'Number(status)') == 1)
                    root.grabWindow().save(str(reports/f'speaker-demo-{mode}-{position}.png'))
            assert bridge.preview_calls == 1
            root.setProperty('narrationRate', 2)
            pump(60)
            assert evaluate(c('narrationConfiguration'), 'entries[2].text') == 'Tốc độ: 112%'
            root.setProperty('narrationRate', 0)
            c('toggleVoiceSlidePreview').clicked.emit()
            pump(100)
            assert root.property('voicePreviewExpanded') and not thumbnail.isVisible()
            assert c('expandedSpeakerPreview').isVisible()
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
                for removed in ('companionReadingOptions', 'companionReadingAuto', 'companionReadingVisible', 'companionReadingFull'):
                    assert companion.findChild(QObject, removed) is None
                assert bridge.teachingSession.state['reading_mode'] == 'auto'
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
            result = dict(status='passed', warnings=warnings, dimensions=dimensions, language_layouts=language_layouts,
                          checks=['light/dark across pages and Settings tabs', 'dialogs inherit dark palette',
                                  'Compact lesson details/actions share a row with 16:9 thumbnail at 1080/1366/1920',
                                  '16:9 thumbnail expands/collapses without repeated render',
                                  'EN/VI/both speaker demo follows all six positions immediately without global loading; preview image reused',
                                  'Template samples open PNGs in-app; selection cards retain thin borders',
                                  'Narration summary stays beside action while scrolling and updates with language/position',
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
