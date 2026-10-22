"""Real Qt/Office: show only an owned fixture, observe speaker windows without global input."""

import json
import sys
import tempfile
import time
from multiprocessing import freeze_support
from pathlib import Path

import win32gui
from PySide6.QtCore import QCoreApplication, QEvent, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from test_teaching_session import prepared_lesson

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.powerpoint import slideshow_handle
from app.teaching_session import prepare_teaching
from app.ui import Bridge
from scripts.qt_result_preview_mascot_smoke import control, pump, until


def visible_speakers(owner):
    result = []

    def collect(hwnd, _):
        if (
            win32gui.IsWindowVisible(hwnd)
            and win32gui.GetClassName(hwnd).startswith("BiliClass.Speakers.")
            and win32gui.GetWindow(hwnd, 4) == owner
        ):
            result.append(hwnd)

    win32gui.EnumWindows(collect, None)
    return result


def main():
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    report = Path(sys.argv[1] if len(sys.argv) > 1 else "reports/speaker-startup")
    report.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bcl-speaker-startup-", ignore_cleanup_errors=True) as folder:
        lesson, preview, directory, source = prepared_lesson(Path(folder))
        original = source.read_bytes()
        prepared = prepare_teaching(lesson, preview, directory)
        library = Library(directory)
        bridge = Bridge(library)
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda rows: warnings.extend(map(str, rows)))
        engine.rootContext().setContextProperty("bridge", bridge)
        engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        try:
            window.show()
            bridge._activate_teaching(prepared)
            until(lambda: bridge.powerpointState.get("opened"), timeout=60)
            bridge.startTeachingShow()
            first_slide = first_speaker = None
            deadline = time.monotonic() + 40
            while time.monotonic() < deadline:
                app.processEvents()
                pump(20)
                hwnd = slideshow_handle(prepared["path"])
                if hwnd and first_slide is None:
                    first_slide = time.monotonic()
                if hwnd and visible_speakers(hwnd):
                    first_speaker = time.monotonic()
                    break
            assert first_slide is not None and first_speaker is not None, bridge.powerpointState
            latency = first_speaker - first_slide
            assert latency < 2.5, latency
            until(lambda: bridge.powerpointState.get("active"))
            assert len(visible_speakers(hwnd)) == 2
            bridge.navigatePowerPoint("next_slide")
            until(lambda: bridge.powerpointState.get("slide") == 2)
            until(lambda: not visible_speakers(hwnd))
            bridge.navigatePowerPoint("next_slide")
            until(lambda: bridge.powerpointState.get("slide") == 3)
            until(lambda: len(visible_speakers(hwnd)) == 1)
            bridge.navigatePowerPoint("previous_slide")
            until(lambda: bridge.powerpointState.get("slide") == 2)
            until(lambda: not visible_speakers(hwnd))
            assert source.read_bytes() == original
            assert not warnings, warnings
            (report / "result.json").write_text(
                json.dumps(
                    dict(
                        status="passed",
                        first_speaker_after_slide_seconds=round(latency, 3),
                        vi_en_silent_slide_transitions=True,
                        source_unchanged=True,
                        no_synthetic_global_input=True,
                        qml_warnings=[],
                    )
                ),
                encoding="utf-8",
            )
            print("Speaker startup Qt + Office smoke passed.", flush=True)
        finally:
            if bridge.powerpoint_worker:
                bridge.stopPowerPoint()
                until(lambda: bridge.powerpoint_worker is None, timeout=30)
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
            companion = control(window, "companionWindow")
            companion.setProperty("disposing", True)
            companion.hide()
            window.hide()
            engine.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            pump(80)
            library.close()


if __name__ == "__main__":
    freeze_support()
    main()
