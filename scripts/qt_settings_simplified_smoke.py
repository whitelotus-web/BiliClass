"""Disposable Qt settings layout and real backup/restore; never touch user data."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPointF, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
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
    reports = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/settings-layout')
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-settings-final-', ignore_cleanup_errors=True) as folder:
        directory = Path(folder)
        library = Library(directory/'original')
        lesson = library.create('Bài thử sao lưu', 'Toán', 'THPT', '11', [('Mở đầu', 'Nội dung gốc.')])
        sample = library.directory/'audio/sample.wav'
        sample.parent.mkdir(exist_ok=True)
        sample.write_bytes(b'backup fixture; no synthesis')
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]

        def c(name):
            return control(window, name)

        def center(item):
            return item.mapToScene(QPointF(item.width()/2, 0)).x()

        try:
            window.setProperty('page', 'settings')
            page = c('settingsPage')
            pump(150)
            c('settingsTeacher').setProperty('text', 'Cô Minh')
            c('settingsSchool').setProperty('text', 'THPT Bình Minh')
            show_profile_before = bridge.settings['show_profile']
            click(window, c('saveProfile'))
            assert bridge.settings['teacher'] == 'Cô Minh'
            assert bridge.settings['show_profile'] == show_profile_before
            assert c('sidebarTeacherName').property('text') == 'Cô Minh'
            assert c('uploadSchoolLogo').property('text') == 'Tải logo trường (PNG/JPG)'
            assert not c('removeSchoolLogo').isVisible() and not c('settingsCurrentLogo').isVisible()
            # Add, replace and remove through the real storage slots in a
            # disposable library. The current image and controls follow state.
            logo = directory/'logo.png'
            Image.new('RGBA', (90, 90), '#0869f9').save(logo)
            bridge.saveSchoolLogo(QUrl.fromLocalFile(str(logo)).toString())
            pump(150)
            assert c('settingsCurrentLogo').isVisible() and c('removeSchoolLogo').isVisible()
            assert c('uploadSchoolLogo').property('text') == 'Thay logo'
            original_logo = (library.directory/'assets/school-logo.png').read_bytes()
            Image.new('RGBA', (90, 90), '#ff7d2b').save(logo)
            bridge.saveSchoolLogo(QUrl.fromLocalFile(str(logo)).toString())
            pump(100)
            assert original_logo != (library.directory/'assets/school-logo.png').read_bytes()
            c('removeSchoolLogo').clicked.emit()
            pump(100)
            assert not bridge.schoolLogoUrl and not c('settingsCurrentLogo').isVisible()
            assert c('uploadSchoolLogo').property('text') == 'Tải logo trường (PNG/JPG)'
            bridge.saveSchoolLogo(QUrl.fromLocalFile(str(logo)).toString())
            pump(100)
            assert window.grabWindow().save(str(reports/'general.png'))
            # Content owns its actions: enlarging the window must not send
            # preview/save buttons to the bottom of the otherwise empty page.
            for mode in ('light', 'dark'):
                bridge.setApplicationTheme(mode)
                for width, height in ((1080, 700), (1366, 850), (1920, 1080)):
                    window.resize(width, height)
                    page.setProperty('activeTab', 0)
                    pump(150)
                    viewport = c('settingsContentScroll').property('contentItem')
                    profile, appearance = c('teacherProfileCard'), c('applicationAppearanceCard')
                    profile_pos, appearance_pos = (item.mapToScene(QPointF()) for item in (profile, appearance))
                    if c('generalSettingsLayout').width() >= 1000:
                        assert abs(profile_pos.y()-appearance_pos.y()) < 1
                        assert appearance_pos.x() >= profile_pos.x()+profile.width()+13
                    else:
                        assert appearance_pos.y() >= profile_pos.y()+profile.height()+13
                    for name in ('applicationThemeLight', 'applicationThemeDark'):
                        choice = c(name)
                        point = choice.mapToItem(appearance, QPointF())
                        assert point.x() >= 0 and point.x()+choice.width() <= appearance.width()
                    for name in ('settingsCurrentLogo', 'uploadSchoolLogo', 'removeSchoolLogo'):
                        item = c(name)
                        point = item.mapToItem(profile, QPointF())
                        assert point.x() >= 0 and point.x()+item.width() <= profile.width()
                    assert viewport.property('contentWidth') <= c('settingsContentScroll').width()+1
                    window.grabWindow().save(str(reports/f'{mode}-general-{width}.png'))
                    page.setProperty('activeTab', 2)
                    pump(150)
                    card, actions, rate = c('multilingualVoiceCard'), c('settingsVoiceActions'), c('settingsVoiceRate')
                    action_pos = actions.mapToItem(card, QPointF())
                    rate_pos = rate.mapToItem(card, QPointF())
                    assert 0 < action_pos.y()-(rate_pos.y()+rate.height()) < 40
                    assert action_pos.y()+actions.height() < card.height()
                    # Scroll on short windows, then verify every action is
                    # reachable without horizontal overflow or changing drafts.
                    viewport.setProperty('contentY', max(0, viewport.property('contentHeight')-viewport.height()))
                    pump(100)
                    for name in ('previewMultilingualVoice', 'stopVoicePreview', 'saveMultilingualVoice'):
                        button = c(name)
                        point = button.mapToItem(viewport, QPointF())
                        assert point.x() >= 0 and point.x()+button.width() <= viewport.width()+1
                        assert point.y() >= 0 and point.y()+button.height() <= viewport.height()+1
                    window.grabWindow().save(str(reports/f'{mode}-voice-{width}.png'))
                    page.setProperty('activeTab', 3)
                    pump(80)
                    assert window.findChild(QObject, 'mascotReducedMotion') is None
                    assert not c('mascotPreview').property('reducedMotion')
                    assert c('mascotAccessories').property('text') == 'Hiện phụ kiện theo môn'
                    c('mascotAccessories').setProperty('checked', False)
                    pump(60)
                    assert not c('mascotAccessorySummary').isVisible()
                    assert not c('mascotAccessorySubject').isVisible() and not c('mascotAccessorySubject').isEnabled()
                    assert not c('mascotPreview').property('accessories')
                    c('mascotAccessories').setProperty('checked', True)
                    pump(60)
                    assert c('mascotAccessorySummary').isVisible() and c('mascotAccessorySubject').isEnabled()
                    pump(150)
                    mascot = c('mascotSettingsContent')
                    assert mascot.width() <= 1180 and abs(center(mascot)-center(page)) < 2
                    viewport.setProperty('contentY', max(0, viewport.property('contentHeight')-viewport.height()))
                    pump(100)
                    guide, bindings, navigation = c('shortcutGuideLayout'), c('shortcutBindings'), c('shortcutNavigationGuide')
                    if guide.property('columns') == 2:
                        gap = navigation.mapToScene(QPointF()).x()-(bindings.mapToScene(QPointF()).x()+bindings.width())
                        assert 31 <= gap <= 33, gap
                    assert window.grabWindow().save(str(reports/f'{mode}-mascot-shortcuts-{width}.png'))
            for width, height in ((1080, 700), (1366, 850), (1920, 1080)):
                window.resize(width, height)
                page.setProperty('activeTab', 1)
                pump(150)
                card, brand = c('aboutBiliClassCard'), c('aboutBiliClassBrand')
                assert abs(center(card)-center(brand)) < 2
                version, copyright = c('aboutBiliClassVersion'), c('aboutBiliClassCopyright')
                update = c('aboutCheckUpdate')
                assert all(abs(center(item)-center(card)) < 2 for item in (version, copyright, update))
                assert brand.mapToScene(QPointF()).y()+brand.height() < version.mapToScene(QPointF()).y()
                assert update.mapToScene(QPointF()).y()+update.height() < copyright.mapToScene(QPointF()).y()
                assert version.mapToScene(QPointF()).y()+version.height() < update.mapToScene(QPointF()).y()
                assert copyright.width() >= 300
                assert window.grabWindow().save(str(reports/f'about-{width}.png'))
                page.setProperty('activeTab', 5)
                pump(100)
                for name in ('settingsBackup', 'settingsRestore', 'relocateLibraryButton'):
                    button = c(name)
                    assert button.isVisible() and button.isEnabled()
                    position = button.mapToScene(QPointF())
                    assert position.x() >= 0 and position.x()+button.width() <= window.width()
                assert not c('settingsReferenceButton').isVisible()
                assert window.grabWindow().save(str(reports/f'data-{width}.png'))
                click(window, c('toggleDataOptions'))
                for name in ('settingsOpenData', 'settingsOpenLibrary', 'settingsSupportReport', 'settingsReferenceButton'):
                    assert c(name).isVisible()
                click(window, c('toggleDataOptions'))
            page.setProperty('activeTab', 2)
            pump(100)
            assert not c('voiceSaveStatus').isVisible(), 'Idle saved settings have no redundant hint'
            # A failed restore cannot switch libraries or quit. A verified backup
            # then restores the real fixture and requests one clean restart.
            invalid = directory/'broken.bcbackup'
            invalid.write_bytes(b'not a backup')
            with patch('app.storage_controls.QGuiApplication.quit') as quit_app:
                bridge.restoreLibraryTo(invalid.as_uri(), directory.as_uri())
                until(lambda: not bridge.busy)
                assert bridge.error and not bridge.storage.next_directory and not quit_app.called
                backup = directory/'teacher-backup.bcbackup'
                bridge.backupLibrary(backup.as_uri())
                until(lambda: not bridge.busy)
                assert backup.is_file() and bridge.storage.state['status'] == 'passed'
                bridge.restoreLibraryTo(backup.as_uri(), directory.as_uri())
                until(lambda: not bridge.busy and bool(bridge.storage.next_directory))
                assert quit_app.call_count == 1
            restored = Path(bridge.storage.next_directory)
            assert restored != library.directory and restored.is_relative_to(directory)
            recovered = Library.read_only(restored)
            try:
                assert recovered.get(lesson['id'])['title'] == lesson['title']
                assert recovered.setting('teacher', '') == 'Cô Minh'
            finally:
                recovered.close()
            assert (restored/'audio/sample.wav').read_bytes() == sample.read_bytes()
            assert library.get(lesson['id'])['revision'] == lesson['revision']
            assert not warnings, warnings
            result = dict(status='passed', warnings=warnings, checks=[
                'General profile/theme columns stack on narrow windows; preview card removed',
                'Logo add/replace/remove updates image, buttons and saved asset',
                'Voice actions remain next to rate controls at 1080/1366/1920, light/dark',
                'Centered brand, version, update action and copyright in that vertical order',
                'Mascot settings stay centered and bounded; shortcut columns remain adjacent',
                'Three main storage actions; advanced actions collapsed and reachable',
                'Profile fields still save; redundant voice hint hidden at rest',
                'Real backup/restore preserves original library, profile and audio',
                'Only successful verified restore requests a clean restart into restored data'])
            (reports/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                           bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                           bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                worker.shutdown()
            c('companionWindow').setProperty('disposing', True)
            c('companionWindow').hide()
            window.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
