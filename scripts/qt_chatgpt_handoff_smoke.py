"""Exercise the browser handoff UI and returned PPTX with isolated teacher data.

Browser launches and the final classroom session are intercepted. PowerPoint
preview rendering is real; there are no network or translation calls.
"""
import hashlib
import json
import sys
import tempfile
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pptx import Presentation
from pptx.util import Inches
from PySide6.QtCore import QMetaObject, QObject, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge

app = QGuiApplication([])
QQuickStyle.setStyle("Basic")
app.setFont(QFont("Arial", 10))
reports = Path("reports/chatgpt-handoff")
reports.mkdir(parents=True, exist_ok=True)
Path(".runtime/chatgpt-smoke").mkdir(parents=True, exist_ok=True)
workspace = Path(tempfile.mkdtemp(prefix="flow-", dir=".runtime/chatgpt-smoke")).resolve()
library = Library(workspace / "library")
source = workspace / "Bài gốc.pptx"
returned = workspace / "Bài ChatGPT trả về.pptx"
deck = Presentation()
for i in range(2):
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    slide.shapes.add_textbox(Inches(.5), Inches(.5), Inches(8), Inches(2)).text = "Bài giảng của thầy cô"
    slide.notes_slide.notes_text_frame.text = "VI: Diện tích bằng 12 cm².\nEN: The area is 12 cm²."
deck.save(source)
deck.save(returned)
digest = hashlib.sha256(returned.read_bytes()).hexdigest()
bridge = Bridge(library)
engine = QQmlApplicationEngine()
warnings, failures, stages, opened = [], [], [], []
engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
engine.rootContext().setContextProperty("bridge", bridge)
engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
assert engine.rootObjects(), warnings
window = engine.rootObjects()[0]
window.setProperty("page", "new")
window.setProperty("selectedFileName", source.name)
window.setProperty("selectedFile", QUrl.fromLocalFile(str(source)).toString())
window.findChild(QObject, "lessonTitle").setProperty("text", "Bài giảng với ChatGPT")
window.findChild(QObject, "lessonSubject").setProperty("text", "Toán")
window.findChild(QObject, "creationLayout").setProperty("currentIndex", 2)
QDesktopServices.openUrl = lambda url: opened.append(url.toString()) or True
deadline = time.monotonic() + 90


def safe(action):
    def run():
        try:
            action()
        except Exception:
            failures.append(traceback.format_exc())
            print(failures[-1], flush=True)
            app.exit(1)
    return run


def click(name):
    target = window.findChild(QObject, name)
    if target is None:
        # Repeater delegates can belong to a QML context outside the QObject tree.
        queue = [window.contentItem()]
        while queue:
            item = queue.pop()
            if item.objectName() == name:
                target = item
                break
            queue.extend(item.childItems())
    assert target and target.property("enabled"), name
    assert QMetaObject.invokeMethod(target, "clicked", Qt.DirectConnection)


def wait_idle(action):
    assert time.monotonic() < deadline, "Flow timed out"
    if bridge.busy:
        QTimer.singleShot(100, safe(lambda: wait_idle(action)))
    else:
        action()


def start():
    assert window.findChild(QObject, "creationLayout").property("visible")
    assert window.findChild(QObject, "creationWorkflow").property("visible")
    assert window.findChild(QObject, "conversionProvider").property("currentIndex") == 0
    assert not window.findChild(QObject, "creationTemplatesButton").property("visible")
    assert QQuickWindow.grabWindow(window).save(str(reports / "new-native.png"))
    window.findChild(QObject, "creationWorkflow").setProperty("currentIndex", 1)
    QTimer.singleShot(150, safe(gallery))


def gallery():
    assert window.findChild(QObject, "creationTemplatesButton").property("visible")
    assert QQuickWindow.grabWindow(window).save(str(reports / "new-template.png"))
    click("creationTemplatesButton")
    QTimer.singleShot(300, safe(gallery_visible))


def gallery_visible():
    dialog = window.findChild(QObject, "templateGallery")
    assert dialog.property("visible")
    plan = window.findChild(QObject, "templateSampleSlide").property("plan")
    assert plan["image"] and not plan["overflow"]
    assert QQuickWindow.grabWindow(window).save(str(reports / "gallery-standard.png"))
    dialog.setProperty("preset", "visual")
    QTimer.singleShot(300, safe(gallery_visual))


def gallery_visual():
    click("templateThumbnail_visual")
    QTimer.singleShot(150, safe(gallery_visual_slide))


def gallery_visual_slide():
    dialog = window.findChild(QObject, "templateGallery")
    plan = window.findChild(QObject, "templateSampleSlide").property("plan")
    assert plan["kind"] == "visual" and plan["image"]
    assert QQuickWindow.grabWindow(window).save(str(reports / "gallery-visual.png"))
    assert QMetaObject.invokeMethod(dialog, "close", Qt.DirectConnection)
    # Keep the configured split view when switching back to the original deck.
    window.findChild(QObject, "creationWorkflow").setProperty("currentIndex", 0)
    click("createLessonButton")
    QTimer.singleShot(100, safe(lambda: wait_idle(prepared)))


def prepared():
    assert not bridge.error, bridge.message
    assert window.property("page") == "chatgpt"
    request = bridge.chatgptRequest
    assert request["config"]["layout"] == "split_view" and request["config"]["level"] == 2
    assert "Hai cột" in request["prompt"] and "Giữ theme" in request["prompt"]
    assert opened == ["https://chatgpt.com/"]
    assert Path(request["bundle"]).is_file()
    assert QQuickWindow.grabWindow(window).save(str(reports / "browser-handoff.png"))
    stages.append("Visible level/layout/workflow -> local prompt/bundle -> browser handoff (intercepted)")
    bridge.receiveChatGPTDeck(QUrl.fromLocalFile(str(returned)).toString())
    QTimer.singleShot(100, safe(lambda: wait_idle(received)))


def received():
    assert not bridge.error, bridge.message
    assert window.property("page") == "result"
    result = bridge.quickResult
    assert result["external"] and result["draft"] and result["image"]
    assert hashlib.sha256(Path(result["path"]).read_bytes()).hexdigest() == digest
    assert not any(s["approved"] for s in bridge.lesson["segments"])
    assert all(s["vi"] and s["en"] for s in bridge.lesson["segments"])
    assert QQuickWindow.grabWindow(window).save(str(reports / "returned-pptx.png"))
    click("useConvertedLessonButton")
    assert window.findChild(QObject, "wholeLessonReview").property("visible")
    sessions = []
    bridge._start_powerpoint_session = lambda *args: sessions.append(args)
    click("confirmWholeLessonButton")
    assert len(sessions) == 1 and all(s["approved"] for s in bridge.lesson["segments"])
    assert not bridge.quickResult["draft"]
    stages.append("Receive byte-identical PPTX -> real Office preview -> whole-deck confirmation -> mascot mapping")
    lesson_id = bridge.lesson["id"]
    bridge.openLesson(lesson_id)
    assert bridge.quickResult["external"] and not bridge.quickResult["draft"]
    assert bridge.quickResult["segment_map"]
    stages.append("Reopen saved presentation retains returned file, confirmation and slide mapping")
    assert not warnings, warnings
    app.exit(0)


QTimer.singleShot(550, safe(start))
code = app.exec()
if bridge.worker:
    bridge.cancel_event.set()
    bridge.worker.wait()
report = {"status": "passed" if code == 0 and not warnings and not failures else "failed",
          "stages": stages, "warnings": warnings, "failures": failures, "scope": "No API, browser uploads or local translation"}
(reports / "qt-flow.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
window.close()
engine.deleteLater()
app.processEvents()
library.close()
print(json.dumps(report, ensure_ascii=False), flush=True)
raise SystemExit(code)
