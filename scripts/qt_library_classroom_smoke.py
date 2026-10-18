"""Exercise bulk library actions and classroom/report/reference entry points.

Uses disposable lessons, a local saved classroom response and mock audio only.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from qt_result_preview_mascot_smoke import click, control, pump, until

from app.classroom_store import ClassroomStore
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge


def value(item, name):
    result = item.property(name)
    return result.toVariant() if hasattr(result, "toVariant") else result


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    report = Path("reports/rc60/management")
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="biliclass-management-", ignore_cleanup_errors=True) as folder:
        library = Library(Path(folder))
        lessons = []
        for index in range(24):
            lesson = library.create(
                "Bài thử " + str(index),
                "Vật lý" if index < 22 else "Tin học",
                "THPT",
                "11",
                [("Slide 1", "Hệ điều hành quản lý tài nguyên.")],
            )
            lessons.append(
                library.edit_segment(
                    lesson["id"],
                    lesson["segments"][0]["id"],
                    lesson["segments"][0]["vi"],
                    "The operating system manages resources.",
                    True,
                )
            )
        library.save_term("Tin học", "hệ điều hành", "operating system")
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        engine.rootContext().setContextProperty("bridge", bridge)
        warnings = []
        engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        def c(name):
            return control(window, name)
        try:
            window.setProperty("page", "library")
            until(lambda: len(bridge.lessons) == 24 and bridge._catalog.worker is None)
            pump(150)
            assert c("librarySelectAll").isVisible()
            assert c("lessonSelect_" + bridge.lessons[0]["id"]).isVisible()
            assert window.findChild(QObject, "librarySelectMode") is None
            click(window, c("librarySelectAll"))
            assert len(value(window, "selectedLessons")) == 24, "Select all must span pages"
            click(window, c("libraryDownloadSelected"))
            assert c("libraryDownloadDialog").property("visible")
            assert len(value(c("libraryDownloadDialog"), "identities")) == 24
            QMetaObject.invokeMethod(c("libraryDownloadDialog"), "close", Qt.DirectConnection)
            pump()
            click(window, c("libraryDeselectAll"))
            assert not value(window, "selectedLessons")
            c("librarySearch").setProperty("text", "vat ly")
            pump()
            click(window, c("librarySelectAll"))
            assert len(value(window, "selectedLessons")) == 22
            c("librarySearch").setProperty("text", "tin hoc")
            pump()
            assert not value(window, "selectedLessons"), "Changing filters must clear selection"
            click(window, c("librarySelectAll"))
            click(window, c("libraryDeleteSelected"))
            assert c("bulkDeleteLessonsDialog").property("visible")
            click(window, c("cancelBulkDeleteLessons"))
            assert len(library.list_lessons()) == 24
            for width, height in ((1080, 700), (1366, 850)):
                window.resize(width, height)
                pump(120)
                toolbar = [
                    c(name)
                    for name in (
                        "librarySubjectFilter",
                        "libraryGradeFilter",
                        "libraryStateFilter",
                        "libraryVoiceFilter",
                        "librarySelectAll",
                        "libraryDeselectAll",
                        "libraryDownloadSelected",
                        "libraryDeleteSelected",
                        "libraryResultCount",
                    )
                ]
                from PySide6.QtCore import QPointF

                centers = [item.mapToScene(QPointF(item.width() / 2, item.height() / 2)) for item in toolbar]
                assert max(p.y() for p in centers) - min(p.y() for p in centers) < 2, (
                    "All filters/actions must share one line"
                )
                assert all(
                    0 <= p.x() - item.width() / 2 and p.x() + item.width() / 2 < width
                    for item, p in zip(toolbar, centers)
                ), "Toolbar clipped in small window"
                assert all(item.height() <= 34 for item in toolbar)
                assert c("librarySelectAll").property("indicator").width() == 16
                count = c("libraryResultCount")
                delete = c("libraryDeleteSelected")
                assert count.mapToScene(QPointF()).x() >= delete.mapToScene(QPointF(delete.width(), 0)).x()
                description, management = c("libraryDescription"), c("libraryManagementButton")
                assert (
                    abs(
                        description.mapToScene(QPointF(0, description.height() / 2)).y()
                        - management.mapToScene(QPointF(0, management.height() / 2)).y()
                    )
                    < 2
                )
                gap = (
                    c("librarySearch").mapToScene(QPointF()).y()
                    - management.mapToScene(QPointF(0, management.height())).y()
                )
                assert 0 <= gap <= 14, "Search should sit directly below the description row"
                assert window.grabWindow().save(str(report / f"library-{width}.png"))
            click(window, c("libraryDeleteSelected"))
            click(window, c("confirmBulkDeleteLessons"))
            until(lambda: len(bridge.lessons) == 22)
            assert len(library.list_lessons(trash=True)) == 2
            QMetaObject.invokeMethod(c("lessonTrashDialog"), "open", Qt.DirectConnection)
            pump()
            click(window, c("trashSelectAll"))
            assert len(value(c("lessonTrashDialog"), "selected")) == 2
            click(window, c("trashPurgeAll"))
            assert len(value(c("purgeTrashDialog"), "identities")) == 2
            click(window, c("cancelPurgeTrash"))
            assert len(library.list_lessons(trash=True)) == 2
            click(window, c("trashRestoreSelected"))
            until(lambda: len(bridge.lessons) == 24 and not bridge.trashedLessons)
            bridge.trashLessons([row["id"] for row in lessons[-2:]])
            until(lambda: len(bridge.trashedLessons) == 2)
            click(window, c("trashSelect_" + lessons[-1]["id"]))
            assert len(value(c("lessonTrashDialog"), "selected")) == 1
            assert window.grabWindow().save(str(report / "trash.png"))
            click(window, c("trashPurgeSelected"))
            click(window, c("confirmPurgeTrash"))
            until(lambda: len(bridge.trashedLessons) == 1)
            click(window, c("trashRestoreAll"))
            until(lambda: len(bridge.lessons) == 23 and not bridge.trashedLessons)
            assert not c("trashPurgeAll").isEnabled() and not c("trashRestoreAll").isEnabled()
            click(window, c("closeLessonTrash"))
            window.setProperty("page", "reports")
            pump(100)
            assert c("reportGoClassroom").isVisible()
            click(window, c("reportGoClassroom"))
            assert window.property("page") == "classroom"
            assert not c("startClassButton").isEnabled()
            bridge.selectLessonForClass(lessons[0]["id"])
            pump(100)
            assert not c("startClassButton").isEnabled(), "Unprepared class must stay blocked"
            click(window, c("classroomPrepareButton"))
            assert c("readinessDialog").property("visible")
            QMetaObject.invokeMethod(c("readinessDialog"), "close", Qt.DirectConnection)
            pump()
            assert window.grabWindow().save(str(report / "classroom.png"))
            library.mark_prepared(lessons[0]["id"], lessons[0]["revision"])
            prepared = library.get(lessons[0]["id"])
            with_questions = dict(prepared)
            with_questions["questions"] = []
            store = ClassroomStore(Path(folder) / "classroom.db")
            session, join = store.create(with_questions, "Lớp 11A thử", "anonymous", 40)
            store.join(session, join)
            store.transition(session, "end")
            store.close()
            window.setProperty("page", "reports")
            pump(100)
            assert c("openSelectedReport").isEnabled()
            assert "Chưa có ngày lưu" not in c("reportSessionPicker").property("displayText")
            click(window, c("openSelectedReport"))
            assert bridge.classroom.selectedReport["id"] == session
            c("reportSearch").setProperty("text", "khong co")
            pump()
            assert not c("openSelectedReport").isEnabled()
            c("reportSearch").setProperty("text", "lop 11a")
            pump()
            assert c("openSelectedReport").isEnabled()
            assert window.grabWindow().save(str(report / "reports.png"))
            window.setProperty("page", "reference")
            pump()
            c("termSearch").setProperty("text", "he dieu hanh")
            pump()
            assert len(value(window, "filteredTerms")) == 1
            c("termSearch").setProperty("text", "khong co")
            pump()
            assert not value(window, "filteredTerms")
            c("termSearch").setProperty("text", "")
            pump()
            assert window.grabWindow().save(str(report / "terms.png"))
            click(window, c("foundationDataTab"))
            pump(250)
            assert window.grabWindow().save(str(report / "knowledge.png"))
            assert not warnings, warnings
            result = {
                "status": "passed",
                "qml_warnings": warnings,
                "checks": [
                    "24 lessons selected across pages",
                    "filtered selection resets",
                    "cancel then atomic trash and restore",
                    "16px checks and one-line toolbar at both sizes",
                    "trash select/cancel purge/restore selected/permanent delete/restore all",
                    "ZIP download dialog exact IDs",
                    "classroom empty/preparation guards and navigation",
                    "saved report search and no-result state",
                    "unaccented term search",
                    "knowledge tab",
                    "1080 and 1366 layouts",
                ],
            }
            (report / "result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(json.dumps(result, ensure_ascii=False), flush=True)
        finally:
            window.close()
            bridge.slidePreview.shutdown()
            bridge.libraryThumbnails.shutdown()
            bridge._catalog.shutdown()
            bridge.browserAI.shutdown()
            bridge.english_reader.shutdown()
            bridge.narration_preparation.shutdown()
            bridge.classroom.shutdown()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            app.processEvents()
            library.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
