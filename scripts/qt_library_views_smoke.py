"""Real Qt list/cards, native first-slide covers and selection routing."""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, QPointF, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from qt_result_preview_mascot_smoke import click, control, pump, until

from app.google_translation import KeyStore
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    report = Path(os.environ.get('BILICLASS_LIBRARY_REPORT', 'reports/rc62/library-views'))
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="biliclass-views-", ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        keys = KeyStore(Path(folder))
        keys.add("AIza" + "a" * 35 + "\nAIza" + "b" * 35)
        keys.reserve(400000, 500000)
        for title, subject, vi, en in [
            (
                "Dao động điều hòa",
                "Vật lý",
                "Vận tốc biến thiên tuần hoàn theo thời gian.",
                "Velocity varies periodically with time.",
            ),
            (
                "Hệ điều hành",
                "Tin học",
                "Hệ điều hành quản lý tài nguyên máy tính.",
                "The operating system manages computer resources.",
            ),
            (
                "Năng lượng trong cuộc sống",
                "Vật lý",
                "Năng lượng có thể chuyển từ dạng này sang dạng khác.",
                "Energy can change from one form to another.",
            ),
        ]:
            lesson = library.create(title, subject, "THPT", "11", [("Slide 1", vi)])
            library.edit_segment(lesson["id"], lesson["segments"][0]["id"], vi, en, True)
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        def c(name):
            return control(window, name)
        try:
            window.setProperty("page", "library")
            until(lambda: len(bridge.lessons) == 3 and bridge._catalog.worker is None)
            pump(200)
            print("Catalog ready", flush=True)
            assert bridge.libraryView == "list" and bridge.libraryThumbnails.worker is None
            identity = bridge.lessons[0]["id"]

            def selected():
                return c("lessonSelect_" + identity).property("checked")

            def point_click(item, x, y):
                point = item.mapToScene(QPointF(x, y)).toPoint()
                QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
                pump(100)

            # Selection must work on text/background as well as the checkbox.
            card = c("lessonCard_" + identity)
            point_click(card, 20, 8)
            assert selected() and card.property("selected")
            click(window, c("lessonTitle_" + identity))
            assert not selected(), "Title click should deselect, not open the lesson"
            click(window, c("lessonNarrationBadge_" + identity))
            assert selected() and not bridge.lesson.get("id")
            click(window, c("lessonSelect_" + identity))
            assert not selected(), "Checkbox must toggle exactly once"
            click(window, c("lessonDownload_" + identity))
            assert c("libraryDownloadDialog").property("visible") and not selected()
            QMetaObject.invokeMethod(c("libraryDownloadDialog"), "close", Qt.DirectConnection)
            assert c("lessonOpen_" + identity).property("text") == "Mở PowerPoint"
            assert c("lessonNarrate_" + identity).property("text") == "Tạo giọng đọc"
            assert window.findChild(QObject, "lessonTeach_" + identity) is None
            click(window, c("lessonMore_" + identity))
            click(window, c("lessonEdit_" + identity))
            assert c("lessonMetadataDialog").property("visible") and not selected()
            QMetaObject.invokeMethod(c("lessonMetadataDialog"), "reject", Qt.DirectConnection)
            click(window, c("lessonDelete_" + identity))
            assert c("deleteLessonDialog").property("visible") and not selected()
            click(window, c("cancelDeleteLessonButton"))
            download = c("lessonDownload_" + identity)
            download.setEnabled(False)
            point_click(download, download.width() / 2, download.height() / 2)
            assert not selected(), "Disabled actions must not select a card"
            download.setEnabled(True)
            narration = c("lessonNarrate_" + identity)
            narration.setEnabled(False)
            point_click(narration, narration.width() / 2, narration.height() / 2)
            assert not selected(), 'A disabled narration action must not select its card'
            narration.setEnabled(True)
            start = card.mapToScene(QPointF(20, 8)).toPoint()
            end = card.mapToScene(QPointF(130, 8)).toPoint()
            QTest.mousePress(window, Qt.LeftButton, Qt.NoModifier, start)
            QTest.mouseMove(window, end, 40)
            QTest.mouseRelease(window, Qt.LeftButton, Qt.NoModifier, end)
            pump(100)
            assert not selected(), "Dragging over a row must not select it"
            assert c("libraryListIcon").isVisible() and not c("libraryGridIcon").isVisible()
            click(window, c("lessonSelect_" + identity))
            click(window, c("libraryViewToggle"))
            print("Grid selected:", bridge.libraryView, window.property("libraryLarge"), flush=True)
            assert bridge.libraryView == "grid"
            assert c("libraryGridIcon").isVisible() and not c("libraryListIcon").isVisible()
            until(
                lambda: len(bridge.libraryCovers.images) == 3 and bridge.libraryThumbnails.worker is None,
                timeout=90,
            )
            assert all(row["image"] for row in bridge.libraryCovers.images.values()), (
                bridge.libraryCovers.images
            )
            print("Native covers ready", flush=True)
            assert not bridge.lesson.get("id"), "Covers must not select/open a lesson"
            until(lambda: library.setting("library_view", "") == "grid")
            assert c("lessonSelect_" + identity).property("checked"), "Switch must retain selection"
            click(window, c("lessonCover_" + identity))
            assert not selected() and not bridge.lesson.get("id"), (
                "Cover must toggle selection without opening the lesson"
            )
            click(window, c("lessonTitle_" + identity))
            assert selected()
            card = c("lessonCard_" + identity)
            point_click(card, 20, 8)
            assert not selected()
            click(window, c("lessonSelect_" + identity))
            assert selected(), "Grid checkbox must toggle exactly once"
            click(window, c("lessonMore_" + identity))
            assert selected() and c("lessonEdit_" + identity).isVisible()
            QTest.keyClick(window, Qt.Key_Escape)
            pump(100)
            click(window, c("lessonDelete_" + identity))
            assert c("deleteLessonDialog").property("visible") and selected()
            click(window, c("cancelDeleteLessonButton"))
            click(window, c("lessonMore_" + identity))
            click(window, c("lessonEdit_" + identity))
            assert c("lessonMetadataDialog").property("visible") and selected()
            QMetaObject.invokeMethod(c("lessonMetadataDialog"), "reject", Qt.DirectConnection)
            click(window, c("lessonDownload_" + identity))
            assert c("libraryDownloadDialog").property("visible")
            assert selected(), "Download action must not toggle selection"
            ids = c("libraryDownloadDialog").property("identities").toVariant()
            assert ids == [identity]
            QMetaObject.invokeMethod(c("libraryDownloadDialog"), "close", Qt.DirectConnection)
            for width, height, columns in ((1080, 700, 2), (1366, 850, 3), (1920, 1080, 4)):
                window.resize(width, height)
                pump(250)
                c("libraryHomeScroll").property("contentItem").setProperty("contentY", 0)
                pump(100)
                assert c("libraryGrid").property("columns") == columns
                cover = c("lessonCover_" + identity)
                assert abs(cover.width() / cover.height() - 16 / 9) < 0.01
                sort = c("lessonSortOrder")
                view = c("libraryViewToggle")
                assert view.width() == view.height() == 40
                pos = view.mapToScene(QPointF())
                assert pos.x() > sort.mapToScene(QPointF()).x() + sort.width()
                assert pos.x() + view.width() < width
                assert abs(pos.y() - sort.mapToScene(QPointF()).y()) < 3
                assert window.grabWindow().save(str(report / f"cards-{width}.png"))
                normal_width = c('lessonCard_' + identity).width()
                search = c('librarySearch')
                assert not c('libraryClearSearch').isVisible()
                for query, count in [('tin hoc', 1), ('vat ly', 2)]:
                    search.setProperty('text', query)
                    pump(300)
                    rows = window.property('libraryResult')['rows']
                    assert len(rows) == count
                    first = c('lessonCard_' + rows[0]['id'])
                    assert abs(first.width() - normal_width) <= 1, (width, query, normal_width, first.width())
                    assert abs(first.mapToScene(QPointF()).x() - c('libraryGrid').mapToScene(QPointF()).x()) <= 1
                    assert c('libraryClearSearch').isVisible()
                    assert window.grabWindow().save(str(report / f'cards-{width}-{count}-results.png'))
                    click(window, c('libraryClearSearch'))
                    assert search.property('text') == '' and search.hasActiveFocus()
                    assert not c('libraryClearSearch').isVisible()
                    pump(200)
                    assert len(window.property('libraryResult')['rows']) == 3
            window.resize(1366, 850)
            pump(200)
            click(window, c('lessonSelect_' + identity))
            click(window, c("libraryViewToggle"))
            pump(150)
            assert bridge.libraryView == "list" and c("lessonSelect_" + identity).property("checked")
            assert c("libraryListIcon").isVisible() and not c("libraryGridIcon").isVisible()
            assert window.grabWindow().save(str(report / "list-1366.png"))
            with_read_only = Library.read_only(Path(folder))
            assert with_read_only.setting("library_view", "") == "list"
            with_read_only.close()
            click(window, c("libraryViewToggle"))
            pump(150)
            assert bridge.libraryThumbnails.worker is None, "Switching back must not reload existing covers"
            c("librarySearch").setProperty("text", "tin hoc")
            pump(400)
            assert len(bridge.libraryThumbnails.wanted) == 1
            assert not c("librarySelectAll").property("checked"), "Filtering clears selection"
            # Clearing a keyword must preserve the independently selected subject filter.
            subject = c('librarySubjectFilter')
            choices = subject.property('model')
            subject.setProperty('currentIndex', next(i for i, row in enumerate(choices) if row['id'] == 'Vật lý'))
            pump(200)
            click(window, c('libraryClearSearch'))
            assert c('librarySearch').property('text') == ''
            assert subject.property('currentValue') == 'Vật lý'
            assert len(window.property('libraryResult')['rows']) == 2
            subject.setProperty('currentIndex', 0)
            c('librarySearch').setProperty('text', 'tin hoc')
            pump(200)
            window.setProperty("page", "home")
            pump(250)
            assert not c("libraryGrid").isVisible()
            assert window.findChild(QObject, "lessonSelectionArea_" + identity) is None
            assert c("homeRecentLesson0").isVisible(), "Home uses compact recent-lesson links"
            assert bridge.libraryCovers.images[identity]["image"], (
                "Leaving the page must retain cached covers"
            )
            assert window.findChild(QObject, "newLibraryLesson") is None
            assert window.findChild(QObject, "homeApplicationHealth") is None
            assert bridge.googleSettings.state["health"]["groups"][0]["level"] == "warning"
            assert bridge.googleSettings.state["keys"][0]["name"] == "Key 1"
            c("libraryHomeScroll").property("contentItem").setProperty("contentY", 180)
            pump(100)
            assert window.grabWindow().save(str(report / "home-health.png"))
            click(window, c("openCompanion"))
            pump(100)
            assert (
                c("companionWindow").isVisible()
                and c("toggleCompanionLabel").property("text") == "Ẩn trợ giảng nổi"
            )
            click(window, c("openCompanion"))
            pump(100)
            assert (
                not c("companionWindow").isVisible()
                and c("toggleCompanionLabel").property("text") == "Mở trợ giảng nổi"
            )
            click(window, c("openCompanion"))
            pump(100)
            c("companionWindow").setProperty("collapsed", False)
            pump(150)
            click(c("companionWindow"), c("hideCompanion"))
            pump(100)
            assert (
                not c("companionWindow").isVisible()
                and c("toggleCompanionLabel").property("text") == "Mở trợ giảng nổi"
            )
            window.setProperty("page", "settings")
            c("settingsPage").setProperty("activeTab", 6)
            pump(150)
            key_id = bridge.googleSettings.state["keys"][0]["id"]
            click(window, c("renameGoogleKey_" + key_id))
            pump(100)
            c("keyDisplayNameInput").setProperty("text", "Gmail riêng")
            QMetaObject.invokeMethod(c("renameGoogleKeyDialog"), "accept", Qt.DirectConnection)
            until(lambda: not bridge.busy)
            assert bridge.googleSettings.state["keys"][0]["name"] == "Key 1 (Gmail riêng)"
            assert bridge.googleSettings.state["keys"][0]["used"] == 400000
            window.setProperty("page", "library")
            pump(200)
            assert bridge.libraryThumbnails.worker is None
            before_open = list(window.property("selectedLessons").toVariant())
            open_id = next(row["id"] for row in bridge.lessons if row["subject"] == "Tin học")
            click(window, c("lessonOpen_" + open_id))
            until(lambda: bridge.teachingSession.state.get('lesson_id') == open_id
                  and bridge.powerpointState.get('opened'), timeout=50)
            assert bridge.lesson["id"] == open_id
            assert not bridge.powerpointState.get('active')
            assert window.property('page') == 'library'
            assert list(window.property("selectedLessons").toVariant()) == before_open
            native_worker = bridge.powerpoint_worker
            click(window, c("lessonNarrate_" + open_id))
            until(lambda: window.property('page') == 'voice' and not bridge.busy)
            assert bridge.powerpoint_worker is native_worker and not bridge.narrationBusy
            assert not warnings, warnings
            result = {
                "status": "passed",
                "qml_warnings": warnings,
                "checks": [
                    "native PowerPoint first-slide images for three disposable lessons",
                    "no active lesson change from covers",
                    "list/grid preference persisted",
                    "selection and exact download IDs survive switch",
                    "filters keep same behavior",
                    "one/two search results retain normal card width and left alignment at 1080/1366/1920",
                    "clear-search button restores results and focus, hides on empty text, preserves other filters",
                    "16:9 covers; 2 columns at 1080, 3 at 1366; single 40px toggle right of sort",
                    "four-square and three-line icons match current mode and swap each click",
                    "home stays list; no duplicate new-lesson button",
                    "cover cache retained across modes and tabs without restarting worker",
                    "home local-budget warning at 80%; rename dialog preserves usage",
                    "mascot sidebar toggle and menu Hide synchronize visibility and label",
                    "Open stays in Library; separate narration button opens configuration without starting voice or rebinding Office",
                ],
            }
            result["checks"].append(
                "row/card background, text and cover toggle selection; checkbox once; actions/disabled actions/menu/drag do not toggle; Open still opens lesson"
            )
            (report / "result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            if bridge.powerpoint_worker is not None:
                bridge.stopPowerPoint()
                until(lambda: bridge.powerpoint_worker is None, timeout=20)
            c("companionWindow").setProperty("disposing", True)
            c("companionWindow").hide()
            window.hide()
            bridge.libraryThumbnails.shutdown()
            bridge.googleSettings.shutdown()
            bridge._library_preferences.shutdown()
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


if __name__ == "__main__":
    raise SystemExit(main())
