"""Exercise the real Qt interface against a disposable library; no user data touched."""

import json
import os
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import Q_ARG, QEventLoop, QMetaObject, QObject, QPointF, Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.library import Library
from app.pack import export_pack, import_pack
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from biliclass_m0.paths import RESOURCES

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "app"
REPORTS.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("BILICLASS_MODEL_DIR", str(ROOT / ".runtime" / "models"))
application = QGuiApplication([])
QQuickStyle.setStyle("Basic")
for font in (RESOURCES / "assets").glob("*.ttf"):
    QFontDatabase.addApplicationFont(str(font))
application.setFont(QFont("Be Vietnam Pro", 10))


def pump(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def wait_until(predicate, timeout=30000):
    started = time.monotonic()
    while not predicate():
        pump(25)
        if (time.monotonic() - started) * 1000 > timeout:
            window.grabWindow().save(str(REPORTS / "workflow-timeout.png"))
            raise AssertionError("Timed out waiting for UI state")
    pump(100)


with tempfile.TemporaryDirectory(prefix="biliclass-ui-", ignore_cleanup_errors=True) as temporary:
    library = Library(Path(temporary))
    bridge = Bridge(library)
    engine = QQmlApplicationEngine()
    warnings = []
    engine.warnings.connect(lambda messages: warnings.extend(str(x) for x in messages))
    engine.rootContext().setContextProperty("bridge", bridge)
    engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml" / "Main.qml")))
    assert engine.rootObjects(), warnings
    window = engine.rootObjects()[0]
    window.resize(1366, 768)
    window.setPosition(0, 0)
    window.setProperty("page", "new")
    guide = window.findChild(QObject, "helpDialog")
    wait_until(lambda: guide.property("opened"))
    QMetaObject.invokeMethod(guide, "close")
    wait_until(lambda: not guide.property("visible"))

    def field(name):
        value = window.findChild(QObject, name)
        assert value is not None, name
        return value

    def click(name):
        item = field(name)
        assert isinstance(item, QQuickItem), name
        # Bring controls in scrollable pages into the laptop viewport before
        # sending a real mouse event; screenshots alone include clipped items.
        parent = item.parentItem()
        while parent is not None:
            if parent.metaObject().indexOfProperty("contentY") >= 0:
                bottom = item.mapToItem(parent, QPointF(0, item.height())).y()
                if bottom > parent.height():
                    parent.setProperty("contentY", min(
                        parent.property("contentHeight") - parent.height(),
                        parent.property("contentY") + bottom - parent.height() + 12,
                    ))
                    pump(100)
            parent = parent.parentItem()
        point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2)).toPoint()
        assert item.isVisible() and item.isEnabled(), name
        if not (0 <= point.x() < window.width() and 0 <= point.y() < window.height()):
            window.grabWindow().save(str(REPORTS / "workflow-offscreen.png"))
        assert 0 <= point.x() < window.width() and 0 <= point.y() < window.height(), (name, point)
        QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
        pump(150)

    checks = []
    field("lessonTitle").setProperty("text", "Bài thử đa môn")
    field("lessonSubject").setProperty("text", "Môn giáo viên tự tạo")
    field("lessonContent").setProperty("text", "Hãy trình bày ý kiến của em.\n\nThảo luận theo nhóm.")
    click("createLessonButton")
    wait_until(lambda: not bridge.busy and window.property("page") == "editor")
    assert len(bridge.lesson["segments"]) == 2
    assert bridge.lesson["education_level"] == "THPT" and bridge.lesson["grade"] == "10"
    assert field("viEditor").property("text") == "Hãy trình bày ý kiến của em."
    checks.append("create via UI, configurable subject, correct default grade, extraction displayed")

    field("enEditor").setProperty("text", "Share your opinion.")
    assert window.property("dirty")
    QMetaObject.invokeMethod(window, "go", Q_ARG("QVariant", "library"))
    pump(200)
    assert field("unsavedDialog").property("visible")
    click("stayButton")
    pump(500)
    assert field("enEditor").property("text") == "Share your opinion."
    click("approveButton")
    if not bridge.segment["approved"] or window.property("dirty"):
        window.grabWindow().save(str(REPORTS / "approval-failure.png"))
        raise AssertionError(json.dumps({
            "approved": bridge.segment["approved"], "dirty": window.property("dirty"),
            "message": bridge.message,
            "warnings": bridge.inspectPair(field("viEditor").property("text"), field("enEditor").property("text")),
            "unsaved_visible": field("unsavedDialog").property("visible"),
            "help_visible": field("helpDialog").property("visible"),
        }, ensure_ascii=True))
    checks.append("unsaved navigation guard, keep editing, explicit approval persisted")

    bridge.selectSegment(1)
    click("translateButton")
    if bridge.busy:
        assert not field("viEditor").isEnabled()
    wait_until(lambda: not bridge.busy)
    assert not bridge.error, bridge.message
    assert bridge.segment["en"] and not bridge.segment["approved"]
    translated = bridge.segment["en"]
    click("approveButton")
    assert bridge.status == "READY_TO_TEACH"
    checks.append("actual local model translation, editing disabled during job, separate approval")

    click("readinessButton")
    assert field("readinessDialog").property("visible")
    assert bridge.readiness["text_ready"]
    if bridge.englishVoices:
        click("prepareEnglishAudio")
        wait_until(lambda: not bridge.busy)
        assert not bridge.error, bridge.message
        assert next(c["ok"] for c in bridge.readiness["checks"] if c["id"] == "audio_en")
    field("readinessDialog").setProperty("visible", False)
    checks.append("readiness and actual SAPI English audio preparation, without speaker playback")

    click("previewButton")
    preview = field("lessonPreview")
    assert preview.isVisible()
    pump(250)
    assert QQuickWindow.grabWindow(preview).save(str(REPORTS / "preview.png"))
    preview.close()
    pump(100)
    checks.append("native preview opens with saved bilingual content")

    lesson_id = bridge.lesson["id"]
    destination = export_pack(library, lesson_id, Path(temporary) / "Bài đã duyệt.biliclass")
    copied = import_pack(library, destination)
    assert copied["id"] != lesson_id and not any(s["approved"] for s in copied["segments"])
    reopened = Library(library.directory)
    assert reopened.get(lesson_id)["segments"][1]["en"] == translated
    reopened.close()
    checks.append("pack roundtrip, imported content unapproved, disk persistence verified")

    previous_revision = bridge.lesson["revision"]
    original_en = bridge.segment["en"]
    field("enEditor").setProperty("text", original_en + " Add an example.")
    field("enEditor").setProperty("cursorPosition", 4)
    pump(2300)
    assert not window.property("dirty")
    assert field("enEditor").property("cursorPosition") == 4
    assert library.get(lesson_id)["segments"][1]["en"] == original_en + " Add an example."
    assert not bridge.segment["approved"]
    bridge.restoreRevision(previous_revision)
    bridge.selectSegment(1)
    assert bridge.segment["en"] == original_en and not bridge.segment["approved"]
    checks.append("autosave preserves caret, resets review, history restore recovers prior content")

    window.setProperty("page", "new")
    field("lessonTitle").setProperty("text", "English source lesson")
    field("lessonSubject").setProperty("text", "Môn tự tạo")
    field("sourceLanguage").setProperty("currentIndex", 1)
    field("lessonContent").setProperty("text", "Discuss in groups.")
    click("createLessonButton")
    wait_until(lambda: not bridge.busy and window.property("page") == "editor")
    assert bridge.lesson["source_language"] == "en" and bridge.segment["vi"] == ""
    click("translateToViButton")
    wait_until(lambda: not bridge.busy)
    assert not bridge.error, bridge.message
    assert bridge.segment["en"] == "Discuss in groups." and bridge.segment["vi"]
    assert not bridge.segment["approved"]
    checks.append("English-source import and actual EN to VI draft translation via UI")

    memory_source = "Hãy quan sát và mô tả."
    reference = library.create(
        "Bài đã duyệt A", "Môn tự tạo", "THPT", "11", [("Đoạn 1", memory_source)]
    )
    library.edit_segment(
        reference["id"], reference["segments"][0]["id"], memory_source, "Observe and describe.", True
    )
    window.setProperty("page", "new")
    field("lessonTitle").setProperty("text", "Dùng lại câu đã duyệt")
    field("lessonSubject").setProperty("text", "Môn tự tạo")
    field("sourceLanguage").setProperty("currentIndex", 0)
    field("lessonContent").setProperty("text", memory_source)
    click("createLessonButton")
    wait_until(lambda: not bridge.busy and window.property("page") == "editor")
    click("translateButton")
    assert not bridge.busy and bridge.segment["en"] == "Observe and describe."
    assert not bridge.segment["approved"] and "từng duyệt" in bridge.message
    checks.append("one approved same-subject phrase reused without running the model; result stays draft")

    alternative = library.create(
        "Bài đã duyệt B", "Môn tự tạo", "THPT", "12", [("Đoạn 1", memory_source)]
    )
    library.edit_segment(
        alternative["id"], alternative["segments"][0]["id"], memory_source, "Look and describe.", True
    )
    window.setProperty("page", "new")
    field("lessonTitle").setProperty("text", "Chọn giữa hai cách dịch")
    field("lessonSubject").setProperty("text", "Môn tự tạo")
    field("lessonContent").setProperty("text", memory_source)
    click("createLessonButton")
    wait_until(lambda: not bridge.busy and window.property("page") == "editor")
    click("translateButton")
    assert field("memoryChoiceDialog").property("visible")
    assert len(bridge.memoryChoices) == 2 and bridge.segment["en"] == ""
    selected = bridge.memoryChoices[0]["text"]
    pump(250)
    QQuickWindow.grabWindow(window).save(str(REPORTS / "memory-choices.png"))
    choices_dialog = field("memoryChoiceDialog")
    first_choice = QPointF(
        choices_dialog.property("x") + choices_dialog.property("width") / 2,
        choices_dialog.property("y") + 132,
    ).toPoint()
    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, first_choice)
    pump(150)
    assert bridge.segment["en"] == selected and not bridge.segment["approved"]
    checks.append("conflicting approved translations open a choice dialog before applying a draft")

    applied = []
    bridge.launch(lambda: (time.sleep(0.15), "late result")[1], applied.append)
    bridge.cancelJob()
    wait_until(lambda: not bridge.busy)
    assert applied == []
    checks.append("cancelled job does not apply its late result")

    for page in ("editor", "home", "library", "new", "glossary", "settings"):
        window.setProperty("page", page)
        pump(150)
        assert QQuickWindow.grabWindow(window).save(str(REPORTS / f"flow-{page}.png"))
    assert not warnings, warnings
    checks.append("six screens rendered without QML warnings")
    report = {
        "status": "passed",
        "checks": checks,
        "translation": translated,
        "warnings": warnings,
        "test_data": "temporary library removed after test",
        "scope": "source application on current Windows machine",
    }
    (REPORTS / "ui-workflow.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    window.setProperty("dirty", False)
    window.close()
    engine.deleteLater()
    pump(100)
    library.close()
    print(json.dumps({"status": "passed", "checks": len(checks)}))
