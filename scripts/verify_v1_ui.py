"""Actual Qt authoring, projector and classroom controls against disposable data."""
import json
import multiprocessing
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    import httpx
    from PySide6.QtCore import QEventLoop, QMetaObject, QObject, QPointF, Qt, QTimer, QUrl
    from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuickControls2 import QQuickStyle
    from PySide6.QtTest import QTest

    from app.library import Library
    from app.paths import RESOURCE_ROOT
    from app.ui import Bridge
    from biliclass_m0.paths import RESOURCES
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    for font in (RESOURCES / "assets").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("Be Vietnam Pro", 10))
    root = Path(__file__).resolve().parents[1] / "reports/app"
    def pump(ms=150):
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()
    def wait(predicate, timeout=35):
        started = time.monotonic()
        while not predicate():
            pump(50)
            assert time.monotonic()-started < timeout, "UI condition timed out"
        pump()
    with tempfile.TemporaryDirectory(prefix="biliclass-v1-ui-", ignore_cleanup_errors=True) as directory:
        library = Library(directory)
        lesson = library.create("Thảo luận dựa trên bằng chứng", "Liên môn", "THPT", "11", [("Hoạt động nhóm", "Dùng bằng chứng để giải thích ý kiến.")])
        library.edit_segment(lesson["id"], lesson["segments"][0]["id"], lesson["segments"][0]["vi"], "Use evidence to explain your ideas.", True)
        bridge = Bridge(library)
        engine, warnings = QQmlApplicationEngine(), []
        engine.warnings.connect(lambda entries: warnings.extend(str(e) for e in entries))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        window.resize(1366, 768)
        bridge.openLesson(lesson["id"])
        pump(500)
        def item(name):
            value = window.findChild(QObject, name)
            assert value is not None, name
            return value
        def click(name):
            target = item(name)
            point = target.mapToScene(QPointF(target.width()/2, target.height()/2)).toPoint()
            assert target.isVisible() and target.isEnabled(), name
            assert 0 <= point.x() < window.width() and 0 <= point.y() < window.height(), (name, point)
            QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
            pump()
        try:
            click("teachingButton")
            item("supportVi").setProperty("text", "Đối chiếu dữ liệu trước khi kết luận.")
            item("supportEn").setProperty("text", "Check the data before making a conclusion.")
            item("supportReview").setProperty("checked", True)
            click("saveSupportButton")
            assert bridge.teaching.items[0]["approved"]
            item("teachingTabs").setProperty("currentIndex", 1)
            pump()
            item("questionVi").setProperty("text", "Điều gì giúp củng cố lập luận?")
            item("questionEn").setProperty("text", "What supports an argument?")
            item("questionOptions").setProperty("text", "Dữ liệu | Data\nPhỏng đoán | Guess | Chưa đối chiếu bằng chứng")
            item("questionReview").setProperty("checked", True)
            click("saveQuestionButton")
            assert len(bridge.teaching.questions) == 1 and bridge.teaching.questions[0]["approved"], bridge.message
            window.grabWindow().save(str(root / "question-authoring.png"))
            QMetaObject.invokeMethod(item("teachingDialog"), "close")
            bridge.teaching.ask("explanation", "en")
            assert bridge.teaching.response["available"]
            preview = item("lessonPreview")
            preview.show()
            pump(350)
            preview.grabWindow().save(str(root / "teaching-console.png"))
            projector = item("projectorWindow")
            bridge.showProjector(projector, 0)
            pump(300)
            projector.grabWindow().save(str(root / "projector.png"))
            projector.hide()
            preview.hide()
            companion = item("companionWindow")
            bridge.showCompanion(companion)
            pump(300)
            companion.grabWindow().save(str(root / "companion.png"))
            companion.hide()
            window.setProperty("page", "classroom")
            bridge.prepareLesson()
            assert bridge.readiness["prepared_ready"], bridge.message
            bridge.classroom.start("Lớp 11A thử nghiệm", "seat", 50, "127.0.0.1", "")
            wait(lambda: not bridge.busy and bridge.classroom.running)
            info = bridge.classroom.runtime.info
            with httpx.Client(trust_env=False) as client:
                student = client.post(f"http://127.0.0.1:{info['port']}/api/join", json={"join": info["join"], "seat": 1})
                assert student.status_code == 200
            question = bridge.teaching.questions[0]
            bridge.classroom.openQuestion(question["id"], 120, "both", False)
            wait(lambda: bool(bridge.classroom.state.get("round")))
            pump(300)
            window.grabWindow().save(str(root / "classroom-teacher.png"))
            projector.setProperty("quiz", True)
            bridge.showProjector(projector, 0)
            pump(300)
            projector.grabWindow().save(str(root / "classroom-projector.png"))
            projector.hide()
            bridge.classroom.action("close")
            wait(lambda: bridge.classroom.state["round"]["status"] == "closed")
            bridge.classroom.action("reveal")
            wait(lambda: bridge.classroom.state["round"]["status"] == "revealed")
            bridge.classroom.action("end")
            wait(lambda: bridge.classroom.state["status"] == "ended")
            bridge.classroom.openReport(info["session_id"])
            window.setProperty("page", "reports")
            pump(300)
            window.grabWindow().save(str(root / "reports.png"))
            assert bridge.classroom.selectedReport["rounds"][0]["answered"] == 0
            assert not warnings, warnings
            result = {"status": "passed", "scope": "1366x768 Qt windows, isolated loopback server", "checks": ["support authoring", "question authoring", "prepared assistance", "teacher console", "projector", "mascot companion", "classroom process and join", "round controls", "saved report"], "qml_warnings": warnings}
            (root / "v1-ui.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps(result))
        finally:
            bridge.classroom.disconnect()
            if bridge.worker:
                bridge.worker.wait()
            for obj in engine.rootObjects():
                obj.hide()
            engine.deleteLater()
            pump()
            bridge.stopSpeech()
            library.close()
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
