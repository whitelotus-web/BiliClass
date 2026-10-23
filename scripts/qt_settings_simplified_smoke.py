"""Disposable Qt settings layout and real backup/restore; never touch user data."""

import json
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QPointF, QSize, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

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
        duplicate = library.directory/'google_jobs/backup-fixture/copy.wav'
        duplicate.parent.mkdir(parents=True)
        duplicate.write_bytes(sample.read_bytes())
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
            heading = c('settingsPageTitle')
            conversion_heading = c('creationPageHeading')
            assert heading.property('font').pixelSize() == conversion_heading.property('font').pixelSize()
            assert abs(page.x() - c('creationScroll').x()) < 1, 'Main tool pages share the same left gutter'
            assert not c('saveProfile').isEnabled(), 'Unchanged profile must not offer a redundant save'
            original_teacher = bridge.settings['teacher']
            click(window, c('settingsTeacher'))
            QTest.keyClick(window, Qt.Key_End)
            QTest.keyClick(window, Qt.Key_X)
            pump(30)
            assert c('saveProfile').isEnabled() and bridge.settings['teacher'] == original_teacher
            c('settingsTeacher').setProperty('text', original_teacher)
            assert not c('saveProfile').isEnabled(), 'Reverting the edit leaves no unsaved change'
            c('settingsTeacher').setProperty('text', 'Cô Minh')
            c('settingsSchool').setProperty('text', 'THPT Bình Minh')
            assert c('saveProfile').isEnabled()
            show_profile_before = bridge.settings['show_profile']
            click(window, c('saveProfile'))
            assert bridge.settings['teacher'] == 'Cô Minh'
            assert not c('saveProfile').isEnabled(), 'Successful save must disable the profile button'
            c('settingsSchool').setProperty('text', 'THPT Mới')
            assert c('saveProfile').isEnabled()
            c('settingsSchool').setProperty('text', bridge.settings['school'])
            assert not c('saveProfile').isEnabled()
            subject = c('settingsSubjects')
            old_index = subject.property('currentIndex')
            subject.setProperty('currentIndex', 0 if old_index != 0 else 1)
            assert c('saveProfile').isEnabled()
            subject.setProperty('currentIndex', old_index)
            assert not c('saveProfile').isEnabled()
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
            assert not c('saveProfile').isEnabled(), 'Logo already saves itself and must not dirty profile fields'
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
                    assert window.findChild(QObject, 'stopVoicePreview') is None
                    for name in ('previewMultilingualVoice', 'saveMultilingualVoice'):
                        button = c(name)
                        point = button.mapToItem(viewport, QPointF())
                        assert point.x() >= 0 and point.x()+button.width() <= viewport.width()+1
                        assert point.y() >= 0 and point.y()+button.height() <= viewport.height()+1
                    window.grabWindow().save(str(reports/f'{mode}-voice-{width}.png'))
                    page.setProperty('activeTab', 3)
                    pump(80)
                    assert c('mascotShortcutsTitle').property('text') == 'Phím tắt Mascot'
                    assert window.findChild(QObject, 'mascotReducedMotion') is None
                    assert not c('mascotPreview').property('reducedMotion')
                    assert c('mascotAccessories').property('text') == 'Hiện phụ kiện theo môn'
                    c('mascotAccessories').setProperty('checked', False)
                    pump(60)
                    # RC132 keeps the subject in place, disabled, so switching
                    # accessories does not shift the settings layout.
                    selected_subject = c('mascotAccessorySubject').property('currentText')
                    assert c('mascotAccessorySummary').isVisible()
                    assert c('mascotAccessorySubject').isVisible() and not c('mascotAccessorySubject').isEnabled()
                    assert not c('mascotPreview').property('accessories')
                    c('mascotAccessories').setProperty('checked', True)
                    pump(60)
                    assert c('mascotAccessorySummary').isVisible() and c('mascotAccessorySubject').isEnabled()
                    assert c('mascotAccessorySubject').property('currentText') == selected_subject
                    pump(150)
                    mascot = c('mascotSettingsContent')
                    assert abs(mascot.width()-mascot.parentItem().width()) < 2
                    assert abs(mascot.mapToItem(mascot.parentItem(), QPointF()).x()) < 2
                    assert window.grabWindow().save(str(reports/f'{mode}-mascot-{width}.png'))
                    viewport.setProperty('contentY', max(0, viewport.property('contentHeight')-viewport.height()))
                    pump(100)
                    guide, bindings, navigation = c('shortcutGuideLayout'), c('shortcutBindings'), c('shortcutNavigationGuide')
                    if guide.property('columns') == 2:
                        gap = navigation.mapToScene(QPointF()).x()-(bindings.mapToScene(QPointF()).x()+bindings.width())
                        assert 39 <= gap <= 41, gap
                        assert abs(bindings.width()-navigation.width()) < 2
                        assert abs(bindings.mapToScene(QPointF()).y()-navigation.mapToScene(QPointF()).y()) < 2
                    else:
                        assert navigation.mapToScene(QPointF()).y() >= bindings.mapToScene(QPointF(0, bindings.height())).y()+23
                    reset, save = c('resetMascotShortcuts'), c('saveMascotShortcuts')
                    action_gap = save.mapToScene(QPointF()).x()-reset.mapToScene(QPointF(reset.width(), 0)).x()
                    assert 9 <= action_gap <= 11
                    panel = c('mascotShortcutPanel')
                    assert abs(save.mapToItem(panel, QPointF(save.width(), 0)).x()-panel.width()) < 2
                    for name in ('shortcutBinden', 'shortcutBindvi', 'shortcutArrowCluster'):
                        item = c(name)
                        point = item.mapToItem(panel, QPointF())
                        assert point.x() >= 0 and point.x()+item.width() <= panel.width()+1
                    assert window.grabWindow().save(str(reports/f'{mode}-mascot-shortcuts-{width}.png'))
            page.setProperty('activeTab', 3)
            window.showMaximized()
            c('settingsContentScroll').property('contentItem').setProperty('contentY', 0)
            pump(250)
            mascot = c('mascotSettingsContent')
            assert abs(mascot.width()-mascot.parentItem().width()) < 2
            assert window.grabWindow().save(str(reports/'mascot-maximized.png'))
            window.showNormal()
            window.resize(1080, 700)
            pump(150)
            assert abs(mascot.width()-mascot.parentItem().width()) < 2
            assert c('settingsContentScroll').property('contentItem').property('contentWidth') <= c('settingsContentScroll').width()+1
            click(window, c('shortcutBinden'))
            QTest.keyClick(window, Qt.Key_A)
            pump(80)
            assert c('saveMascotShortcuts').isEnabled()
            click(window, c('saveMascotShortcuts'))
            assert bridge.mascotShortcuts.state['bindings']['en'] == 'A'
            assert library.setting('mascot_shortcuts', {})['en'] == 'A'
            click(window, c('resetMascotShortcuts'))
            assert bridge.mascotShortcuts.state['bindings']['en'] == 'Space'
            assert not c('saveMascotShortcuts').isEnabled()
            for width, height in ((1080, 700), (1366, 850), (1920, 1080)):
                window.resize(width, height)
                page.setProperty('activeTab', 1)
                pump(150)
                for mode in ('light', 'dark'):
                    bridge.setApplicationTheme(mode)
                    pump(100)
                    card, info, brand = (c(name) for name in ('aboutBiliClassCard', 'aboutBiliClassInfo', 'aboutBiliClassBrand'))
                    artwork = c('aboutBiliClassArtwork')
                    assert card.property('artworkReady'), 'Supplied artwork must load from app assets'
                    assert artwork.width() == card.width() and artwork.height() == card.height()
                    assert info.x() > 0 and info.x()+info.width() < card.width()*0.45, 'Leave both mascots unobstructed'
                    assert info.y() >= 23 and info.y()+info.height() <= card.height()-23
                    version, copyright = c('aboutBiliClassVersion'), c('aboutBiliClassCopyright')
                    update = c('aboutCheckUpdate')
                    assert all(abs(center(item)-center(info)) < 2 for item in (brand, version, copyright, update))
                    # Measure the painted group, not a full-width layout that
                    # could still leave its logo and text stuck to the left.
                    logo, brand_text = c('aboutBiliClassLogo'), c('aboutBiliClassBrandText')
                    group_center = (logo.mapToScene(QPointF()).x()+brand_text.mapToScene(QPointF(brand_text.width(), 0)).x())/2
                    assert abs(group_center-center(info)) < 2
                    brand_pos = brand.mapToItem(info, QPointF())
                    assert brand_pos.x() >= 0 and brand_pos.x()+brand.width() <= info.width()+1
                    assert brand.mapToScene(QPointF()).y()+brand.height() < version.mapToScene(QPointF()).y()
                    assert update.mapToScene(QPointF()).y()+update.height() < copyright.mapToScene(QPointF()).y()
                    assert version.mapToScene(QPointF()).y()+version.height() < update.mapToScene(QPointF()).y()
                    assert copyright.width() >= 300
                    assert version.property('color').name() == '#112650', 'Keep dark text readable on the light artwork in both themes'
                    assert copyright.property('color').name() == '#112650'
                    description = c('aboutBiliClassDescription')
                    assert description.property('text') == ('Chuyển đổi bài giảng song ngữ, hỗ trợ trình chiếu\n'
                                                            'với giọng đọc, mascot trợ giảng và thư viện lưu trữ ngay trên máy.')
                    assert description.property('lineCount') == 2
                    assert abs(center(description)-center(card if card.property('footerBelow') else info)) < 2
                    assert description.y()+description.height() <= card.height()-23
                    assert window.grabWindow().save(str(reports/f'{mode}-about-{width}.png'))
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
            # A high-DPI laptop can have fewer than 1080 logical pixels. Use a
            # smaller test window without changing the actual Windows display.
            window.setMinimumSize(QSize(860, 620))
            window.resize(860, 620)
            page.setProperty('activeTab', 1)
            for mode in ('light', 'dark'):
                bridge.setApplicationTheme(mode)
                pump(150)
                card, info = c('aboutBiliClassCard'), c('aboutBiliClassInfo')
                assert info.x()+info.width() < card.width()*0.45
                description = c('aboutBiliClassDescription')
                assert description.property('lineCount') == 2
                assert description.property('contentWidth') <= description.width()+1
                assert abs(center(description)-center(card)) < 2
                assert description.y()+description.height() <= card.height()-23
                for item in info.findChildren(QQuickItem):
                    if item.property('text'):
                        point = item.mapToItem(info, QPointF())
                        assert point.x() >= -1 and point.x()+item.width() <= info.width()+1
                        content_width = item.property('contentWidth')
                        if content_width is not None:
                            assert content_width <= item.width()+1, item.property('text')
                viewport = c('settingsContentScroll').property('contentItem')
                assert viewport.property('contentWidth') <= c('settingsContentScroll').width()+1
                assert window.grabWindow().save(str(reports/f'{mode}-about-laptop-top.png'))
                viewport.setProperty('contentY', max(0, viewport.property('contentHeight')-viewport.height()))
                pump(100)
                contact = c('aboutBiliClassContact')
                point = contact.mapToItem(viewport, QPointF())
                assert point.y() >= 0 and point.y()+contact.height() <= viewport.height()+1
                assert window.grabWindow().save(str(reports/f'{mode}-about-laptop-bottom.png'))
            window.setMinimumSize(QSize(1080, 700))
            window.resize(1366, 850)
            page.setProperty('activeTab', 1)
            pump(100)
            update = c('aboutCheckUpdate')
            bridge._set_update_state(downloading=True)
            assert not update.isEnabled(), 'Do not start another check while downloading'
            bridge._set_update_state(downloading=False)
            with patch('app.ui.check_for_update', return_value=None) as check:
                click(window, update)
                until(lambda: bridge.update_worker is None)
                assert check.call_count == 1 and check.call_args.kwargs == {'include_current': True}
                assert update.isEnabled() and not bridge.updateState['checking']
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
                with zipfile.ZipFile(backup) as archive:
                    manifest = json.loads(archive.read('manifest.json'))
                    assert manifest['version'] == 3
                    assert manifest['aliases'] == {'google_jobs/backup-fixture/copy.wav': 'audio/sample.wav'}
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
            assert (restored/'google_jobs/backup-fixture/copy.wav').read_bytes() == sample.read_bytes()
            assert library.get(lesson['id'])['revision'] == lesson['revision']
            assert not warnings, warnings
            result = dict(status='passed', warnings=warnings, checks=[
                'General profile/theme columns stack on narrow windows; preview card removed',
                'Logo add/replace/remove updates image, buttons and saved asset',
                'Voice actions remain next to rate controls at 1080/1366/1920, light/dark',
                'Supplied mascot artwork loads; brand, version, updater and copyright fit the empty left area at 1080/1366/1920, light/dark',
                '860-pixel laptop: logo and wrapped labels stay inside the left area; no horizontal overflow; contact reachable by scrolling',
                'Updated description stays on two centered lines at all four window sizes; narrow windows place it below the artwork at readable font size',
                'About updater still checks through the real slot; disabled during download, enabled again on completion (network mocked)',
                'Mascot fills the content width; shortcut groups have equal columns on wide windows, stack on narrow windows and keep actions together at the right',
                'Three main storage actions; advanced actions collapsed and reachable',
                'Profile fields still save; redundant voice hint hidden at rest',
                'Real backup/restore preserves original library, profile and audio',
                'Duplicate contents stored once; restored into both original paths',
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
