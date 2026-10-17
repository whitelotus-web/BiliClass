"""Exercise the existing six settings tabs with a disposable lesson library."""

import json
import sys
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import QEventLoop, QMetaObject, QObject, QPointF, Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from biliclass_m0.paths import RESOURCES


def pump(ms=150):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def until(predicate, timeout=90):
    started = time.monotonic()
    while not predicate():
        pump(40)
        assert time.monotonic() - started < timeout, "Settings UI timed out"
    pump(100)


def main():
    layout_only = "--layout-only" in sys.argv
    reports = Path(__file__).resolve().parents[1] / "reports" / "app"
    reports.mkdir(parents=True, exist_ok=True)
    app = QGuiApplication([])
    from app.branding import configure_application
    configure_application(app)
    assert not app.windowIcon().isNull()
    QQuickStyle.setStyle("Basic")
    for path in (RESOURCES / "assets").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(path))
    app.setFont(QFont("Be Vietnam Pro", 10))
    checks = []
    with tempfile.TemporaryDirectory(prefix="biliclass-settings-", ignore_cleanup_errors=True) as directory, tempfile.TemporaryDirectory(prefix="biliclass-settings-export-") as exports:
        library = Library(Path(directory))
        library.set_setting("class_name", "Lớp cũ không nên tự điền")
        library.set_setting("level", 4)
        lesson = library.create("Bài đa môn", "Môn tự chọn", "THPT", "10", [("Mở đầu", "Hãy thảo luận theo nhóm.")])
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda entries: warnings.extend(str(item) for item in entries))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml" / "Main.qml")))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        window.resize(1366, 850)
        bridge.openLesson(lesson["id"])
        window.setProperty("page", "settings")
        pump(350)

        def control(name):
            item = window.findChild(QObject, name)
            if item is None:
                queue = [window.contentItem()]
                while queue:
                    current = queue.pop()
                    if current.objectName() == name:
                        item = current
                        break
                    queue.extend(current.childItems())
            assert item is not None, name
            return item

        def click(name):
            item = control(name)
            parent = item.parentItem()
            while parent is not None:
                if parent.metaObject().indexOfProperty("contentY") >= 0:
                    top = item.mapToItem(parent, QPointF(0, 0)).y()
                    bottom = item.mapToItem(parent, QPointF(0, item.height())).y()
                    if top < 0:
                        parent.setProperty("contentY", max(0, parent.property("contentY") + top - 12))
                        pump(100)
                    elif bottom > parent.height():
                        parent.setProperty("contentY", min(parent.property("contentHeight") - parent.height(), parent.property("contentY") + bottom - parent.height() + 12))
                        pump(100)
                parent = parent.parentItem()
            point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2)).toPoint()
            if not 0 <= point.y() < window.height():
                viewport = control("settingsContentScroll").property("contentItem")
                top = item.mapToItem(viewport, QPointF(0, 0)).y()
                maximum = max(0, viewport.property("contentHeight") - viewport.height())
                viewport.setProperty("contentY", min(maximum, max(0, viewport.property("contentY") + top - 80)))
                pump(180)
                point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2)).toPoint()
            assert item.isVisible() and item.isEnabled(), name
            assert 0 <= point.x() < window.width() and 0 <= point.y() < window.height(), (name, point)
            QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
            pump(130)

        def shot(name):
            assert window.grabWindow().save(str(reports / f"settings-{name}.png"))

        assert all(control(f"settingsTab{i}") for i in range(6))
        assert control("uploadSchoolLogo").mapToScene(QPointF(0, 0)).y() < control("saveProfile").mapToScene(QPointF(0, 0)).y()
        control("settingsTeacher").setProperty("text", "Cô Minh")
        control("settingsSchool").setProperty("text", "THPT Bình Minh")
        control("settingsSubjects").setProperty("currentIndex", bridge.conversionSubjects.index("Ngữ văn"))
        assert control("savedProfileTeacher").property("text") == "Thầy cô"
        assert control("savedProfileSubjects").property("text") == "Chưa thêm bộ môn"
        click("saveProfile")
        assert bridge.settings["teacher"] == "Cô Minh"
        assert bridge.settings["school"] == "THPT Bình Minh"
        assert bridge.settings["subjects"] == ["Ngữ văn"]
        assert control("savedProfileTeacher").property("text") == "Cô Minh"
        assert control("savedProfileSchool").property("text") == "THPT Bình Minh"
        assert "Ngữ văn" in control("savedProfileSubjects").property("text")
        assert "Cô Minh" in control("projectorProfile").property("text")
        from PIL import Image
        logo = Path(directory) / "sample-logo.png"
        Image.new("RGBA", (90, 90), "#0869f9").save(logo)
        assert control("uploadSchoolLogo")
        bridge.saveSchoolLogo(QUrl.fromLocalFile(str(logo)).toString())
        assert (Path(directory) / "assets" / "school-logo.png").is_file()
        assert bridge.schoolLogoUrl
        assert control("previewSchoolLogo").property("source").toString().startswith("file:")
        assert control("projectorSchoolLogo").property("source").toString().startswith("file:")
        assert control("savedProfileLogo").property("source").toString().startswith("file:")
        control("settingsShowProfile").setProperty("checked", False)
        click("saveProfile")
        assert bridge.settings["show_profile"] is False
        assert control("projectorProfile").property("visible") is False
        assert "Đang ẩn" in control("savedProfileVisibility").property("text")
        control("settingsShowProfile").setProperty("checked", True)
        click("saveProfile")
        assert control("projectorProfile").property("visible") is True
        shot("general")
        checks.append("core settings tabs; multi-subject teacher profile and school logo persist; projector profile can be hidden")

        click("settingsTab1")
        assert control("aboutBiliClassCard").isVisible()
        assert control("aboutBiliClassVersion").property("text") == bridge.appVersion
        assert control("aboutBiliClassCopyright").property("text") == "Copyright © 2026 Nguyễn Diệu Linh"
        assert control("aboutBiliClassLogo").property("source").toString().endswith('brand/biliclass.svg')
        assert control("aboutCheckUpdate")
        assert window.findChild(QObject, "checkUpdatesButton") is None
        assert window.findChild(QObject, "settingsConversionFormat3") is None
        assert window.findChild(QObject, "settingsLevel4") is None
        assert window.findChild(QObject, "saveLevel") is None
        assert "level" not in bridge.settings
        shot("about")
        window.resize(1080, 700)
        pump(250)
        assert control("aboutBiliClassCopyright").width() > 250
        shot("about-small")
        window.resize(1366, 850)
        pump(200)
        checks.append("About replaces bilingual guide; logo, actual version, copyright and updater; window icon; 1080px layout")
        assert bridge.lesson["level"] == 2

        click("settingsTab2")
        assert control("multilingualVoiceCard").isVisible()
        assert len(bridge.multilingualVoices) == 6
        assert not window.findChild(QObject, "voiceEnglishCard")
        assert not window.findChild(QObject, "voiceVietnameseCard")
        original = dict(bridge.voiceSettings)
        click("selectMultilingualVoice2")
        assert bridge.voiceSettings == original, "Selection must remain a draft until saved"
        settings_page = control("settingsPage")
        control("settingsVoiceRate").setProperty("value", 2)
        assert QMetaObject.invokeMethod(control("settingsVoiceRate"), "moved", Qt.DirectConnection)
        assert settings_page.property("draftRate") == 2
        assert bridge.voiceSettings == original, "Speed preview must not change saved preferences"
        if not layout_only:
            click("previewMultilingualVoice")
            until(lambda: bridge.voiceUiState['phase'] in {'playing', 'error'})
            assert "nghe thử" in bridge.message.lower(), bridge.message
            assert bridge.voiceSettings == original
            bridge.stopSpeech()
        click("saveMultilingualVoice")
        until(lambda: not bridge.voiceUiState['saving'])
        assert bridge.voiceSettings["en"] == bridge.voiceSettings["vi"] == "vieneu:Hải Đăng"
        assert bridge.voiceSettings["rate"] == 2
        assert library.setting("voice_options", {}) == {"voice": "vieneu:Hải Đăng", "rate": 2}
        shot("voice")
        checks.append("Single VieNeu speaker for VI/EN; draft choice/speed; explicit atomic save" +
                      ("; playback skipped explicitly" if layout_only else "; actual mixed-language speed preview"))

        click("settingsTab3")
        shot("mascot-top")
        assert bridge.mascotSettings["show_explanation"] and bridge.mascotSettings["show_quiz"]
        click("mascotLumi")
        click("mascotPreviewMode1")
        assert control("mascotPreview").property("expression") == "thinking"
        click("mascotPreviewMode2")
        assert control("mascotPreview").property("expression") == "celebrate"
        control("mascotSubject").setProperty("currentIndex", bridge.conversionSubjects.index('Khác'))
        control('mascotSubjectMode').setProperty('currentIndex', 1)
        control("mascotOtherSubject").setProperty("text", "Môn tự chọn")
        assert control("mascotPreview").property("subject") == "Môn tự chọn"
        control("mascotSize").setProperty("value", 140)
        control("mascotPosition").setProperty("currentIndex", 1)
        control("mascotAccessories").setProperty("checked", False)
        control("mascotReducedMotion").setProperty("checked", False)
        control("mascotExplanation").setProperty("checked", False)
        control("mascotQuiz").setProperty("checked", False)
        click("mascotPreviewMode1")
        assert not control("mascotPreview").property("visible")
        click("mascotPreviewMode2")
        assert not control("mascotPreview").property("visible")
        click("mascotPreviewMode0")
        assert control("mascotPreview").property("visible")
        control("mascotVisible").setProperty("checked", False)
        click("saveMascot")
        assert bridge.settings["mascot"] == "Lumi"
        assert bridge.mascotSettings == {"visible": False, "size": 140, "position": "left", "reduced_motion": False, "accessories": False, "show_explanation": False, "show_quiz": False, 'subject_mode': 'fixed', 'subject': 'Môn tự chọn', 'always_on_top': True}
        assert not control("companionWindow").isVisible()
        assert not control("mascotProjectorLeft").property("visible")
        assert not control("mascotProjectorRight").property("visible")
        control("mascotVisible").setProperty("checked", True)
        click("saveMascot")
        assert control("companionWindow").isVisible(), "Saving an enabled mascot should show the floating assistant"
        assert control("openCompanion").isVisible(), "The main window should keep a mascot launcher available"
        control("companionWindow").hide()
        assert control("mascotProjectorLeft").property("visible")
        assert not control("mascotProjectorRight").property("visible")
        projector = control("projectorWindow")
        projector.setProperty("quiz", True)
        pump(80)
        assert not control("mascotProjectorLeft").property("visible")
        projector.setProperty("quiz", False)
        pump(80)
        assert control("mascotProjectorLeft").property("visible")
        bridge._lesson = library.edit_segment(lesson["id"], bridge.segment["id"], "Hãy thảo luận theo nhóm.", "Discuss in groups.", True)
        bridge.changed.emit()
        assert bridge.teaching.saveSupport("", "explanation", "Giải thích", "Explanation", True)
        bridge.teaching.ask("explanation", "en")
        pump(80)
        assert bridge.teaching.response["available"]
        assert not control("mascotProjectorLeft").property("visible")
        bridge.teaching.reset()
        pump(80)
        assert control("mascotProjectorLeft").property("visible")
        bridge.showProjector(projector, 0)
        pump(250)
        assert control("mascotProjectorLeft").isVisible()
        assert projector.grabWindow().save(str(reports / "settings-mascot-projector.png"))
        projector.hide()
        companion = control("companionWindow")
        companion.setProperty("collapsed", False)
        bridge.showCompanion(companion)
        pump(250)
        assert control("mascotCompanion").property("character") == "Lumi"
        assert control("mascotCompanion").width() >= 130
        assert companion.x() <= 30
        companion.hide()
        shot("mascot")
        window.resize(1080, 700)
        control("settingsContentScroll").property("contentItem").setProperty("contentY", 0)
        pump(200)
        shot("mascot-compact")
        click("mascotLumi")
        pump(150)
        preview_top = control("mascotMiniSlide").mapToScene(QPointF(0, 0)).y()
        assert 250 <= preview_top < window.height() - 50, preview_top
        assert 85 <= control("mascotPreview").width() <= 120
        shot("mascot-compact-preview")
        window.resize(1366, 850)
        pump(160)
        checks.append("mascot cards, context preview, subject label, visibility, explanation/quiz, size and position apply across teacher/projector/companion")

        click("settingsTab4")
        control("settingsClassMode").setProperty("currentIndex", 1)
        control("settingsClassCapacity").setProperty("value", 42)
        click("saveClassroom")
        assert bridge.classroomSettings["mode"] == "seat"
        assert bridge.classroomSettings["capacity"] == 42
        shot("classroom")
        checks.append("classroom mode and capacity persist")

        click("settingsTab5")
        click("settingsBackup")
        assert control("backupSaveDialog").property("visible")
        QMetaObject.invokeMethod(control("backupSaveDialog"), "reject")
        backup_path = Path(exports) / "settings-check.bcbackup"
        bridge.backupLibrary(QUrl.fromLocalFile(str(backup_path)).toString())
        until(lambda: not bridge.busy)
        assert "sao lưu" in bridge.message.lower(), bridge.message
        assert backup_path.is_file()
        shot("data")
        checks.append("data tab creates isolated library backup")

        window.setProperty("page", "classroom")
        pump(200)
        assert control("classTitle").property("text") == ""
        assert control("classMode").property("currentIndex") == 1
        assert control("classSize").property("value") == 42
        checks.append("class name is entered per session; classroom defaults persist")

        window.setProperty("page", "new")
        pump(180)
        control("lessonTitle").setProperty("text", "Bài kiểm tra cấu hình")
        control("lessonSubject").setProperty("currentIndex", bridge.conversionSubjects.index("Sinh học"))
        control("lessonContent").setProperty("text", "Hãy quan sát mẫu vật.")
        control("creationFormat").setProperty("currentIndex", len(bridge.conversionFormats) - 1)
        control("creationGrade").setProperty("currentIndex", 2)
        assert control("creationFormat").property("currentIndex") == len(bridge.conversionFormats) - 1
        assert control("creationGrade").property("currentText") == "12"
        # This test has no API key and must not send a translation request.
        # qt_google_translation_smoke covers the new API workflow separately.
        assert not bridge.chatgptRequest
        checks.append("new lesson uses its local grade/method; no account or uploads in settings smoke")

        assert not warnings, warnings
        report_name = "settings-layout-ui.json" if layout_only else "settings-ui.json"
        (reports / report_name).write_text(json.dumps({"status": "passed", "checks": checks, "qml_warnings": warnings,
                                                      "voice_playback": "skipped" if layout_only else "passed"}, ensure_ascii=False, indent=2), encoding="utf-8")
        window.close()
        bridge.classroom.shutdown()
        bridge.voice_controls.shutdown()
        library.close()
        del engine
        reopened = Library(Path(directory))
        try:
            assert reopened.setting("teacher", "") == "Cô Minh"
            assert reopened.setting("school", "") == "THPT Bình Minh"
            assert reopened.setting("teaching_subjects", []) == ["Ngữ văn"]
            assert (Path(directory) / "assets" / "school-logo.png").is_file()
            assert reopened.setting("mascot", "") == "Lumi"
            assert reopened.setting("voice_options", {}) == {"voice": "vieneu:Hải Đăng", "rate": 2}
            assert reopened.setting("classroom_options", {})["capacity"] == 42
        finally:
            reopened.close()
    print(json.dumps({"status": "passed", "checks": len(checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
