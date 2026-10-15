"""Real Qt conversion lifecycle with blocked/failed speech, no web submission."""

import json
import logging
import sys
import tempfile
import time
from pathlib import Path
from threading import Event
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pptx import Presentation  # noqa: E402
from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlApplicationEngine  # noqa: E402
from PySide6.QtQuickControls2 import QQuickStyle  # noqa: E402

from app.browser_accounts import BrowserAccounts  # noqa: E402
from app.browser_automation import read_record, write_record  # noqa: E402
from app.chatgpt_handoff import prepare_request  # noqa: E402
from app.library import Library  # noqa: E402
from app.lesson_import import save_conversion  # noqa: E402
from app.ui import Bridge  # noqa: E402


def main():
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    entered, release, ticks, failures, warnings = Event(), Event(), [], [], []
    importing, allow_import, import_ticks = Event(), Event(), []
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="bcl-qt-audio-") as temporary:
        root = Path(temporary)
        source = root / "fixture.pptx"
        deck = Presentation()
        for index in range(2):
            slide = deck.slides.add_slide(deck.slide_layouts[6])
            slide.shapes.add_textbox(914400, 914400, 6000000, 1200000).text = f"The force acts on the object. Slide {index+1}."
        deck.save(source)
        library = Library(root / "data")
        store = BrowserAccounts(library.directory)
        account = store.add("Local fixture")
        store.observe(account["id"], "free")
        request = prepare_request(library.directory, {
            "title": "Audio lifecycle fixture", "subject": "Vật lý", "education_level": "THPT", "grade": "11",
            "level": 2, "layout": "split_view", "preset": "standard", "style": "source", "mode": "level",
            "provider": "browser_web"}, source)
        folder = request["folder"]
        write_record(folder, {"account_id": account["id"], "state": "prepared", "url": "", "followups": 0})

        def convert(*args, **kwargs):
            write_record(folder, {"account_id": account["id"], "state": "completed", "url": "https://chatgpt.com/c/fixture", "followups": 0})
            return {"path": str(source), "account_id": account["id"], "cached": True}

        def synthesize(*args):
            entered.set()
            assert release.wait(10), "Test did not release synthesis"
            raise RuntimeError("Deliberate local voice failure")

        def save(*args):
            importing.set()
            assert allow_import.wait(15), "GUI did not remain responsive during import"
            return save_conversion(*args)

        try:
            with patch("app.speech.list_voices", return_value=[{"id": "vieneu:Mai Anh", "provider": "vieneu"}]), \
                 patch("app.browser_dispatch.convert_available", side_effect=convert), \
                 patch("app.slide_quality.render_quality"), \
                 patch("app.lesson_import.save_conversion", side_effect=save), \
                 patch("app.speech.synthesize_background", side_effect=synthesize), \
                 patch.object(Bridge, "previewConvertedSlide"):
                bridge = Bridge(library)
                bridge._chatgpt_request = request
                engine = QQmlApplicationEngine()
                engine.warnings.connect(lambda items: warnings.extend(str(x) for x in items))
                engine.rootContext().setContextProperty("bridge", bridge)
                engine.load(str(ROOT / "app/qml/Main.qml"))
                assert engine.rootObjects(), "QML root missing"
                bridge._run_web_conversion()
                timer = QTimer()
                timer.setInterval(20)
                checked = False
                voice_requested = False
                deadline = time.monotonic() + 35

                def tick():
                    nonlocal checked, voice_requested
                    ticks.append(time.monotonic())
                    if importing.is_set() and not allow_import.is_set():
                        import_ticks.append(time.monotonic())
                        if len(import_ticks) >= 5:
                            allow_import.set()
                    if bridge._lesson and not bridge.busy and not voice_requested:
                        try:
                            assert bridge._browser_state["percent"] == 100
                            assert not entered.is_set() and not bridge.narrationBusy
                            assert bridge.lessonNarration["status"] == "none"
                            voice_requested = True
                            bridge.createLessonNarration("en")
                        except BaseException as exc:
                            failures.append(str(exc))
                            release.set()
                            app.quit()
                    if entered.is_set() and not checked:
                        try:
                            record = read_record(folder, account["id"])
                            lesson = library.get(record["lesson_id"])
                            assert lesson["external_deck"]["reviewed_revision"] == 0
                            assert not bridge.busy and not bridge._browser_running
                            assert bridge._browser_state["percent"] == 100
                            assert bridge.quickResult["path"] and bridge.narrationPreparation["running"]
                            checked = True
                        except BaseException as exc:
                            failures.append(str(exc))
                        finally:
                            release.set()
                    if checked and bridge.narration_preparation.worker is None:
                        try:
                            assert bridge.narrationPreparation["failed"] > 0
                            assert read_record(folder, account["id"])["lesson_id"] == lesson_id[0]
                        except BaseException as exc:
                            failures.append(str(exc))
                        app.quit()
                    if time.monotonic() > deadline:
                        failures.append(f"Qt lifecycle timed out: {bridge.message}; busy={bridge.busy}; lesson={bool(bridge._lesson)}")
                        allow_import.set()
                        release.set()
                        app.quit()

                lesson_id = [""]
                bridge.changed.connect(lambda: lesson_id.__setitem__(0, bridge._lesson.get("id", "")))
                timer.timeout.connect(tick)
                timer.start()
                app.exec()
                bridge.narration_preparation.shutdown()
                bridge.browserAI.shutdown()
                bridge.english_reader.shutdown()
                if bridge.worker is not None:
                    bridge.worker.wait()
                engine.rootObjects()[0].close()
                del engine
                assert checked and len(import_ticks) >= 5 and not failures, failures
                assert not warnings, warnings[:3]
                report = {"status": "passed", "elapsed_seconds": round(time.monotonic()-started, 2),
                          "qt_ticks": len(ticks), "import_heartbeat_ticks": len(import_ticks),
                          "scope": "Worker import keeps GUI responsive; saved PowerPoint pauses without voice; explicit EN generation remains responsive; voice failure cannot undo lesson or approve it; real QML, no web submission"}
                path = ROOT / "reports/app/narration-preparation.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                print(json.dumps(report))
        finally:
            allow_import.set()
            release.set()
            library.close()
            logging.shutdown()


if __name__ == "__main__":
    main()
