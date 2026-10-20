"""Disposable Qt range/drag selection and pinned library controls; no Office/input hooks."""

import json
import os
import tempfile
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QPointF, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
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
    reports = Path(os.environ.get('BILICLASS_SELECTION_REPORT', 'reports/rc100/library-selection'))
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bcl-selection-', ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        for n in range(8):
            library.create(f'Bài thử {n + 1}', 'Vật lý', 'THPT', '10', [('Slide 1', 'Nội dung bài học.')])
        bridge = Bridge(library)
        # Cover rendering is independently covered by qt_library_views_smoke.
        bridge.libraryThumbnails.request = lambda *_: None
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty('bridge', bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/Main.qml')))
        assert engine.rootObjects(), warnings
        root = engine.rootObjects()[0]
        root.resize(1080, 700)
        root.requestActivate()

        def c(name):
            return control(root, name)

        def ids():
            value = root.property('selectedLessons')
            return list(value.toVariant() if hasattr(value, 'toVariant') else value)

        def point(item, x=20, y=8):
            return item.mapToScene(QPointF(x, y)).toPoint()

        def clear():
            root.setProperty('selectedLessons', [])
            root.setProperty('librarySelectionAnchor', '')

        try:
            root.setProperty('page', 'library')
            until(lambda: len(bridge.lessons) == 8 and bridge._catalog.worker is None)
            # Mixed status/title/date fixtures expose independently sized row
            # columns. Selection and the stored lesson records remain real.
            labels = ('Đã lưu bài', 'Sẵn sàng trình chiếu', 'Chưa có lời đọc')
            for index, row in enumerate(bridge._catalog._active):
                row['review'] = {**row.get('review', {}), 'label': labels[index % 3]}
                row['created_at'] = f'2026-10-{index+10:02}T{index+10:02}:54:00+07:00'
                if index == 0:
                    row['title'] += ' – Dao động tắt dần, dao động cưỡng bức và hiện tượng cộng hưởng'
            bridge.lessonsChanged.emit()
            pump(150)
            ordered = root.property('libraryResult')['ids']
            for mode in ('light', 'dark'):
                bridge.setApplicationTheme(mode)
                for width, height in ((1080, 700), (1366, 850), (1920, 1080)):
                    root.resize(width, height)
                    pump(180)
                    dates = [c('lessonCreated_'+identity) for identity in ordered]
                    positions = [item.mapToScene(QPointF()).x() for item in dates]
                    assert max(positions)-min(positions) < 1, (width, positions)
                    for identity in ordered:
                        date, card = c('lessonCreated_'+identity), c('lessonCard_'+identity)
                        assert date.width() >= 140
                        assert date.mapToItem(card, QPointF()).x()+date.width() < card.width()
                    root.grabWindow().save(str(reports/f'{mode}-aligned-dates-{width}.png'))
            root.resize(1080, 700)
            pump(120)
            for mode in ('list', 'grid'):
                bridge.setLibraryView(mode)
                pump(200)
                view = c('libraryHomeScroll').property('contentItem')
                view.setProperty('contentY', 0)
                clear()
                first = c('lessonCard_'+ordered[0])
                QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, point(first))
                assert ids() == [ordered[0]]
                target = c('lessonCard_'+ordered[4])
                # Scroll without changing the anchor, then Shift-click the fifth lesson.
                view.setProperty('contentY', max(0, target.y()-20))
                pump(150)
                QTest.mouseClick(root, Qt.LeftButton, Qt.ShiftModifier, point(target))
                pump(80)
                assert set(ids()) == set(ordered[:5]), (mode, ids())
                # Shift + checkbox also selects the same range, in reverse order.
                view.setProperty('contentY', 0)
                clear()
                first_check = c('lessonSelect_'+ordered[0])
                QTest.mouseClick(root, Qt.LeftButton, Qt.NoModifier, point(first_check, 8, 8))
                assert ids() == [ordered[0]], (mode, ids())
                target_check = c('lessonSelect_'+ordered[2])
                view.setProperty('contentY', max(0, c('lessonCard_'+ordered[2]).y()-20))
                pump(120)
                QTest.mouseClick(root, Qt.LeftButton, Qt.ShiftModifier, point(target_check, 8, 8))
                pump(80)
                assert set(ids()) == set(ordered[:3]), (mode, ids())
                clear()
                view.setProperty('contentY', 0)
                pump(120)
                start = point(c('lessonCard_'+ordered[0]))
                viewport = c('libraryHomeScroll')
                bottom = viewport.mapToScene(QPointF(30, viewport.height()-8)).toPoint()
                QTest.mousePress(root, Qt.LeftButton, Qt.NoModifier, start)
                QTest.mouseMove(root, start + (bottom-start)/2, 60)
                QTest.mouseMove(root, bottom, 60)
                until(lambda: set(ordered[:5]).issubset(ids()), timeout=8)
                QTest.mouseRelease(root, Qt.LeftButton, Qt.NoModifier, bottom)
                pump(120)
                assert not root.property('libraryDragActive')
                assert c('libraryDownloadSelected').isEnabled() and c('libraryDeleteSelected').isEnabled()
                header = c('libraryPinnedHeader')
                top = header.mapToScene(QPointF())
                view.setProperty('contentY', max(0, view.property('contentHeight')-view.height()))
                pump(200)
                assert header.mapToScene(QPointF()) == top
                search = c('librarySearch')
                assert search.isVisible() and search.mapToScene(QPointF()).y() < viewport.y()
                assert c('libraryDeleteSelected').mapToScene(QPointF()).y() < viewport.y()
                last_card = c('lessonCard_'+ordered[-1])
                last = last_card.mapToScene(QPointF())
                viewport_top = viewport.mapToScene(QPointF()).y()
                assert last.y() < viewport_top + viewport.height() and last.y() + last_card.height() > viewport_top
                assert root.grabWindow().save(str(reports/f'{mode}-scrolled.png'))
                if mode == 'list':
                    for width, height, limit in ((1080, 700, 132), (1366, 850, 110)):
                        root.resize(width, height)
                        view.setProperty('contentY', 0)
                        pump(180)
                        assert c('lessonCard_'+ordered[0]).height() <= limit
                        assert c('lessonOpen_'+ordered[0]).height() == 34
                        assert root.grabWindow().save(str(reports/f'compact-list-{width}.png'))
                    root.resize(1080, 700)
                    pump(100)
                search.setProperty('text', 'Bài thử 2')
                pump(150)
                assert not ids() and not root.property('librarySelectionAnchor')
                click(root, c('libraryClearSearch'))
                pump(150)
            selected = library.get(ordered[0])
            for button in ('mouse', 'keyboard'):
                c('librarySearch').forceActiveFocus()
                bridge._show_lesson(selected, auto_repair=False, load_preview=False)
                pump(120)
                assert root.property('page') == 'result'
                if button == 'mouse':
                    QTest.mouseClick(root, Qt.BackButton, Qt.NoModifier, root.contentItem().mapToScene(QPointF(600, 300)).toPoint())
                else:
                    QTest.keyClick(root, Qt.Key_Backspace)
                pump(120)
                if root.property('page') != 'library':
                    focus = root.activeFocusItem()
                    print({'button': button, 'active': root.isActive(), 'focus': focus.objectName() if focus else None,
                           'shortcut': control(root, 'lessonBackspaceShortcut').property('enabled')}, flush=True)
                assert root.property('page') == 'library', button
            bridge._show_lesson(selected, auto_repair=False, load_preview=False)
            component = QQmlComponent(engine)
            component.setData(b'import QtQuick; import QtQuick.Controls; TextField { text: "abc"; width: 220; height: 40; x: 260; y: 140 }', QUrl())
            field = component.create()
            assert field is not None, component.errors()
            field.setParentItem(root.contentItem())
            field.forceActiveFocus()
            QTest.keyClick(root, Qt.Key_Backspace)
            pump(100)
            assert field.property('text') == 'ab' and root.property('page') == 'result'
            field.setParentItem(None)
            field.deleteLater()
            badge_component = QQmlComponent(engine, QUrl.fromLocalFile(str(RESOURCE_ROOT/'qml/LibraryVoiceBadge.qml')))
            badge = badge_component.create()
            assert badge is not None, badge_component.errors()
            cases = [({'ready': True, 'mode': 'vi'}, 'VI'), ({'ready': True, 'mode': 'en'}, 'EN'),
                     ({'ready': True, 'mode': 'both'}, 'VI · EN'),
                     ({'ready': True, 'mode': 'vi', 'variants': [{'ready': True, 'mode': 'en'}, {'ready': False, 'mode': 'vi'}]}, 'EN'),
                     ({'variants': [{'ready': True, 'mode': 'vi'}, {'ready': True, 'mode': 'en'}]}, 'VI · EN'),
                     ({'status': 'partial', 'mode': 'both', 'ready_languages': ['vi']}, 'Giọng chưa đủ')]
            for audio, expected in cases:
                badge.setProperty('audio', audio)
                assert badge.property('text') == expected
            badge.deleteLater()
            assert not warnings, warnings
            result = {'status': 'passed', 'checks': ['Shift-click and Shift-checkbox select the filtered ordered range',
                      'Mixed status labels, long titles and dates align at 1080/1366/1920 in light/dark',
                      'drag selection in list/grid; automatic scrolling at bottom edge',
                      'search, filters and bulk actions remain fixed while lessons scroll',
                      'mouse Back and Backspace return from lesson; text fields still delete text',
                      'compact rows retain metadata and 34px actions at 1080/1366; speaker badge advertises only ready saved languages',
                      'filter changes clear selection and its anchor; no QML warnings'], 'warnings': warnings}
            (reports/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            root.setProperty('page', 'home')
            for worker in (bridge._catalog, bridge.browserAI, bridge.slidePreview, bridge.libraryThumbnails,
                           bridge.narrationPreferences, bridge.narration_preparation, bridge.english_reader,
                           bridge.voice_controls, bridge._companion_preferences, bridge.classroom):
                worker.shutdown()
            companion = c('companionWindow')
            companion.setProperty('disposing', True)
            companion.hide()
            root.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()


if __name__ == '__main__':
    main()
