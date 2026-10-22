"""Render borderless library speaker states and exercise their real hit targets."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge

from .qt_result_preview_mascot_smoke import click, control, pump, until


def colored_pixels(window, item, *, green):
    image = window.grabWindow()
    ratio = image.devicePixelRatio()
    origin = item.mapToScene(QPointF()) * ratio
    count = 0
    for x in range(round(origin.x()), round(origin.x() + item.width() * ratio)):
        for y in range(round(origin.y()), round(origin.y() + item.height() * ratio)):
            color = image.pixelColor(x, y)
            if green:
                count += color.green() > color.red() + 25 and color.green() > color.blue() + 8
            else:
                count += color.blue() > color.green() + 25 and color.blue() > color.red() + 25
    return count


def icon_in(badge, name):
    pending = list(badge.childItems())
    while pending:
        item = pending.pop()
        if item.objectName() == name:
            return item
        pending.extend(item.childItems())
    raise AssertionError(name)


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle('Basic')
    report = Path('reports/rc143/library-speakers')
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='biliclass-speaker-ui-', ignore_cleanup_errors=True) as temporary:
        library = Library(Path(temporary))
        modes = {}
        for mode, title in [('none', 'Chưa có giọng'), ('vi', 'Giọng Việt'), ('en', 'Giọng Anh'), ('both', 'Việt và Anh')]:
            lesson = library.create(title, 'Toán', 'THPT', '11', [('Slide 1', 'Nội dung thử.')])
            library.edit_segment(lesson['id'], lesson['segments'][0]['id'], 'Nội dung thử.', 'Test content.', True)
            modes[lesson['id']] = mode
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(RESOURCE_ROOT / 'qml/Main.qml')
        root = engine.rootObjects()[0]
        checks = []
        try:
            root.resize(1366, 950)
            root.setProperty('page', 'library')
            until(lambda: len(bridge.lessons) == 4 and bridge._catalog.worker is None)
            # Fixture only the verified audio statuses; paint, layout and actions remain real Qt.
            for row in bridge._catalog._active:
                mode = modes[row['id']]
                row['narration'] = {'mode': mode, 'ready': mode != 'none', 'status': 'ready' if mode != 'none' else 'none'}
            bridge._catalog.changed.emit()
            with patch.object(Bridge, 'requestLibraryCovers'), patch.object(Bridge, 'openLessonNarration') as opened:
                for theme in ('light', 'dark'):
                    bridge.setApplicationTheme(theme)
                    for view in ('list', 'grid'):
                        if bridge.libraryView != view:
                            click(root, control(root, 'libraryViewToggle'))
                        pump(250)
                        sizes = set()
                        for identity, mode in modes.items():
                            button = control(root, 'lessonStatus_' + identity)
                            surface = control(root, 'lessonStatusSurface_' + identity)
                            badge = control(root, 'lessonNarrationBadge_' + identity)
                            assert surface.property('color').alpha() == 0
                            sizes.add((button.width(), button.height()))
                            if mode != 'none':
                                icons = [icon_in(badge, 'libraryVoiceIcon_' + language)
                                         for language in ('vi', 'en') if mode in (language, 'both')]
                                assert len(icons) == (2 if mode == 'both' else 1)
                                for icon in icons:
                                    assert icon.isVisible() and icon.width() == 24 and icon.height() == 22
                                    assert colored_pixels(root, icon, green=True) > 20
                                    assert colored_pixels(root, icon, green=False) == 0
                            else:
                                icon = icon_in(badge, 'libraryVoiceSpeakerIcon')
                                assert icon.isVisible() and icon.property('source').toString().endswith('speaker-off.svg')
                                assert colored_pixels(root, icon, green=True) == 0
                            before = opened.call_count
                            click(root, button)
                            assert opened.call_count == before + 1
                            assert opened.call_args.args == (identity,)
                            assert not root.property('selectedLessons').toVariant()
                        assert len(sizes) == 1 and next(iter(sizes)) == (96, 28)
                        assert root.grabWindow().save(str(report / f'{theme}-{view}.png'))
                        focus = control(root, 'lessonStatus_' + next(iter(modes)))
                        focus.forceActiveFocus(Qt.TabFocusReason)
                        pump(100)
                        assert focus.hasActiveFocus()
                        assert colored_pixels(root, focus, green=False) > 20, 'Keyboard focus remains visible'
                        checks.append({'theme': theme, 'view': view, 'hitbox': [96, 28], 'states': list(modes.values())})
            assert not warnings, warnings
            result = {'status': 'passed', 'qml_warnings': warnings, 'states': checks,
                      'checks': ['green ready artwork, gray crossed no-voice', 'transparent background',
                                 'equal hit targets and correct action, no selection side effect', 'visible keyboard focus']}
            (report / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            control(root, 'companionWindow').setProperty('disposing', True)
            root.hide()
            for name in ('libraryThumbnails', 'googleSettings', '_library_preferences', 'slidePreview', '_catalog',
                         'browserAI', 'english_reader', 'narration_preparation', 'narrationPreferences',
                         '_companion_preferences', 'classroom', 'voice_controls', 'inputDocuments'):
                getattr(bridge, name).shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
