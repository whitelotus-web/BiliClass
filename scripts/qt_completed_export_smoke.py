"""Finish narration and auto-save a real voiced PPTX in a disposable library."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from test_teaching_session import prepared_lesson

from app.branding import configure_application
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import click, control, pump, until


def main():
    app = QGuiApplication([])
    configure_application(app)
    QQuickStyle.setStyle("Basic")
    for font in (RESOURCE_ROOT / "assets").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("Be Vietnam Pro", 10))
    report = Path(sys.argv[1] if len(sys.argv) > 1 else "reports/completed-export")
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bcl-auto-export-", ignore_cleanup_errors=True) as folder:
        lesson, preview, directory, source = prepared_lesson(Path(folder))
        original = source.read_bytes()
        wavs = {p.name: p.read_bytes() for p in (directory / "audio").glob("*.wav")}
        library = Library(directory)
        library.set_setting("voice_options", {"voice": lesson["narration"]["voice"], "rate": 0})
        bridge = Bridge(library)
        bridge.previewConvertedSlide = lambda *_: None  # Preview rendering is independently covered.
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]

        def c(name):
            return control(window, name)

        try:
            window.resize(1366, 850)
            window.show()
            bridge._show_lesson(lesson, preview, auto_repair=False, load_preview=False, destination="voice")
            window.setProperty("voiceResultDismissed", False)
            state = {
                **lesson["narration"],
                "lesson_id": lesson["id"],
                "revision": lesson["revision"],
                "running": False,
                "complete": lesson["narration"]["total"],
                "failed": 0,
                "cancelled": False,
            }
            with patch("app.speech.synthesize", side_effect=AssertionError("No synthesis during export")):
                bridge.narration_preparation.state = state
                bridge._narration_updated()
                until(lambda: not bridge.busy and bridge.completedExport.get("phase") == "saved", timeout=30)
            target = Path(bridge.completedExport["path"])
            assert target.parent == source.parent and target != source and target.is_file()
            with ZipFile(target) as archive:
                # Equal silent fixture WAVs share a single embedded media part.
                assert any(p.endswith(".wav") for p in archive.namelist())
            assert bridge.completedExport["coverage"]["speakers"] == 3
            until(lambda: bridge.lessonNarration.get("ready"))
            window.setProperty("voiceResultDismissed", False)
            bridge.narrationChanged.emit()
            until(lambda: c("narrationResultPage").isVisible())
            for theme in ("light", "dark"):
                bridge.setApplicationTheme(theme)
                for width, height in ((1080, 700), (1366, 850)):
                    window.resize(width, height)
                    pump(100)
                    labels = [
                        item
                        for item in window.findChildren(QObject, "completedExportMessage")
                        if item.isVisible()
                    ]
                    assert labels and str(target) in labels[0].property("text")
                    assert "cạnh file gốc" in labels[0].property("text")
                    assert window.grabWindow().save(str(report / f"auto-saved-{theme}-{width}.png"))
            opened = []
            with patch(
                "app.ui.QDesktopServices.openUrl",
                side_effect=lambda url: opened.append(url.toLocalFile()) or True,
            ):
                controls = [
                    item
                    for item in window.findChildren(QObject, "openCompletedExportFolder")
                    if item.isVisible()
                ]
                click(window, controls[0])
            assert [Path(path) for path in opened] == [source.parent], opened
            click(window, c("narrationResultDownload"))
            pump(80)
            assert c("presentationSaveDialog").property("visible"), "Manual Save As remains available"
            assert QMetaObject.invokeMethod(c("presentationSaveDialog"), "reject")
            count = len(list(source.parent.glob("*.pptx")))
            bridge._narration_updated()
            pump(150)
            assert not bridge.busy and len(list(source.parent.glob("*.pptx"))) == count
            bridge._lesson = {}
            bridge.selectionChanged.emit()
            pump(60)
            assert not bridge.completedExport, "Do not show another lesson output"
            assert source.read_bytes() == original
            assert wavs == {p.name: p.read_bytes() for p in (directory / "audio").glob("*.wav")}
            assert not warnings, warnings
            (report / "result.json").write_text(
                json.dumps(
                    dict(
                        status="passed",
                        automatic_without_download_click=True,
                        beside_source=True,
                        standalone_embedded_speakers=3,
                        manual_save_dialog_unchanged=True,
                        repeated_notification_does_not_duplicate=True,
                        source_wavs_preserved=True,
                        qml_warnings=[],
                    )
                ),
                encoding="utf-8",
            )
            print("Completed voice automatic export Qt flow passed.", flush=True)
        finally:
            bridge._completed_export_timer.stop()
            until(lambda: not bridge.busy, timeout=30)
            for service in (
                bridge._catalog,
                bridge.browserAI,
                bridge.slidePreview,
                bridge.libraryThumbnails,
                bridge.narrationPreferences,
                bridge.narration_preparation,
                bridge.english_reader,
                bridge.voice_controls,
                bridge._companion_preferences,
                bridge.classroom,
            ):
                service.shutdown()
            c("companionWindow").setProperty("disposing", True)
            c("companionWindow").hide()
            window.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            pump(80)
            library.close()


if __name__ == "__main__":
    main()
