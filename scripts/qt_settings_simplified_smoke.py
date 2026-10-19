"""Disposable Qt settings layout and real backup/restore; never touch user data."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QPointF, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    reports = Path('reports/rc100/settings-final')
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
            c('settingsShowProfile').setProperty('checked', False)
            click(window, c('saveProfile'))
            assert bridge.settings['teacher'] == 'Cô Minh' and not bridge.settings['show_profile']
            assert c('savedProfileTeacher').property('text') == 'Cô Minh'
            assert window.grabWindow().save(str(reports/'general.png'))
            for width, height in ((1080, 700), (1366, 850), (1920, 1080)):
                window.resize(width, height)
                page.setProperty('activeTab', 1)
                pump(150)
                card, brand = c('aboutBiliClassCard'), c('aboutBiliClassBrand')
                assert abs(center(card)-center(brand)) < 2
                version, copyright = c('aboutBiliClassVersion'), c('aboutBiliClassCopyright')
                assert abs((center(version)+center(copyright))/2-center(card)) < 2
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
                'Centered brand, balanced version/copyright at 1080/1366/1920',
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
