"""Isolated Qt account/settings flow, one-click processing, real Office + voice.

ChatGPT web conversion is intercepted here; tests/test_browser_ai.py exercises
the actual browser upload/download adapter against a routed fixture separately.
"""

import faulthandler
import hashlib
import json
import tempfile
import time
import traceback
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches
from PySide6.QtCore import QMetaObject, QObject, Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from app import browser_ai_ui, browser_automation, speech
from app.chatgpt_handoff import load_request
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import Bridge

app = QGuiApplication([])
faulthandler.dump_traceback_later(60, repeat=True)
QQuickStyle.setStyle("Basic")
app.setFont(QFont("Arial", 10))
reports = Path("reports/browser-ai")
reports.mkdir(parents=True, exist_ok=True)
Path(".runtime/browser-ai-smoke").mkdir(parents=True, exist_ok=True)
workspace = Path(tempfile.mkdtemp(prefix="qt-", dir=".runtime/browser-ai-smoke")).resolve()
library = Library(workspace / "library")
source = workspace / "Bài gốc.pptx"
deck = Presentation()
slide = deck.slides.add_slide(deck.slide_layouts[6])
slide.shapes.add_textbox(Inches(.5), Inches(.5), Inches(8), Inches(2)).text = "Xin chào. / Hello."
slide.notes_slide.notes_text_frame.text = "VI: Xin chào.\nEN: Hello.\nCHECK: Nội dung thử, chưa phải bài thật."
deck.save(source)
digest = hashlib.sha256(source.read_bytes()).hexdigest()
bridge = Bridge(library)
engine = QQmlApplicationEngine()
warnings, failures, stages, requests = [], [], [], []
engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
engine.rootContext().setContextProperty("bridge", bridge)
engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
assert engine.rootObjects(), warnings
window = engine.rootObjects()[0]
window.setProperty("page", "settings")
settings = window.findChild(QObject, "settingsPage")
settings.setProperty("activeTab", 6)
# First load of both native voice models can be slow on an external drive.
deadline = time.monotonic() + 600


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
    assert target and target.property("enabled"), name
    assert QMetaObject.invokeMethod(target, "clicked", Qt.DirectConnection)


def wait_idle(action):
    assert time.monotonic() < deadline, "Browser AI flow timed out"
    if bridge.busy:
        QTimer.singleShot(150, safe(lambda: wait_idle(action)))
    else:
        action()


def converted(account, root, folder, cancel, progress, **kwargs):
    request = load_request(folder)
    assert account["label"] == "ChatGPT 1" and account["channel"] == "msedge"
    assert request["config"]["level"] == 3 and request["config"]["layout"] == "split_view"
    assert request["config"]["style"] == "source"
    assert "3.000" in request["prompt"] and "Giữ theme" in request["prompt"] and "CHECK:" in request["prompt"]
    requests.append(request)
    progress("Đang chờ ChatGPT · chế độ kiểm thử, không gửi ra mạng")
    cancel.wait(.6)
    return {"path": str(source), "url": "https://chatgpt.com/c/fixture-123"}


browser_automation.convert = converted


def login_fixture(account, root, cancel, progress, url, *, auto_close):
    assert auto_close and account["channel"] == "msedge"
    progress("Đang đăng nhập · kiểm thử, không truy cập web")
    cancel.wait(.25)
    return {"ready": True, "plan": "plus" if account["label"] == "ChatGPT 1" else "free", "message": "Đã đăng nhập và tự lưu."}


browser_ai_ui.login = login_fixture


def wait_login(action):
    assert time.monotonic() < deadline, "Login timed out"
    if bridge.browserAI.loginBusy:
        QTimer.singleShot(80, safe(lambda: wait_login(action)))
    else:
        action()


def accounts():
    assert not window.findChild(QObject, "browserAccountLabel")
    assert not window.findChild(QObject, "browserAccountChannel")
    assert not window.findChild(QObject, "browserOptionsSave")
    assert not window.findChild(QObject, "browserLoginFinish")
    click("browserAccountAdd")
    assert bridge.browserAI.loginBusy
    QTimer.singleShot(350, safe(lambda: wait_login(second_account)))


def second_account():
    assert len(bridge.browserAI.accounts) == 1 and bridge.browserAI.accounts[0]["ready"]
    click("browserAccountAdd")
    QTimer.singleShot(350, safe(lambda: wait_login(accounts_ready)))


def accounts_ready():
    first, second = [a["id"] for a in bridge.browserAI.accounts]
    assert len(bridge.browserAI.accounts) == 2
    assert bridge.browserAI.store.preferred()["id"] == first
    resume = workspace / "resume"
    resume.mkdir()
    (resume / "browser-job.json").write_text(json.dumps({"account_id": second}), encoding="utf-8")
    assert bridge.browserAI.conversionAccount(str(resume))["id"] == second
    bridge.browserAI.remove(second)
    assert len(bridge.browserAI.accounts) == 1 and bridge.browserAI.activeId == first
    assert bridge.browserAI.automatic and bridge.browserAI.audio
    assert bridge.browserAI.accounts[0]["plan"] == "plus"
    assert QQuickWindow.grabWindow(window).save(str(reports / "accounts.png"))
    stages.append("Login-only tab: one button creates Edge profile, saves login automatically; Plus priority; no browser/options/save/finish controls")
    window.setProperty("page", "new")
    window.setProperty("selectedFileName", source.name)
    window.setProperty("selectedFile", QUrl.fromLocalFile(str(source)).toString())
    window.findChild(QObject, "lessonTitle").setProperty("text", "Bài thử Browser AI")
    window.findChild(QObject, "lessonSubject").setProperty("text", "Liên môn")
    window.findChild(QObject, "creationLevel").setProperty("currentIndex", 3)
    window.findChild(QObject, "creationLayout").setProperty("currentIndex", 2)
    QTimer.singleShot(200, safe(start))


def start():
    assert QQuickWindow.grabWindow(window).save(str(reports / "one-click.png"))
    click("createLessonButton")
    QTimer.singleShot(150, safe(capture_progress))


def capture_progress():
    assert QQuickWindow.grabWindow(window).save(str(reports / "waiting.png"))
    QTimer.singleShot(150, safe(lambda: wait_idle(received)))


def received():
    assert not bridge.error, bridge.message
    assert len(requests) == 1 and window.property("page") == "result"
    assert bridge.browserState["phase"] == "completed"
    assert bridge.quickResult["external"] and bridge.quickResult["draft"] and bridge.quickResult["image"]
    assert hashlib.sha256(Path(bridge.quickResult["path"]).read_bytes()).hexdigest() == digest
    assert bridge.lesson["segments"][0]["vi"] == "Xin chào." and bridge.lesson["segments"][0]["en"] == "Hello."
    assert not any(s["approved"] for s in bridge.lesson["segments"])
    narration = bridge.browserState["audio"]
    assert narration["complete"] == 2 and not narration["failed"], narration
    audio_files = list((library.directory / "audio").glob("*.wav"))
    assert len(audio_files) == 2 and all(speech.valid_audio(p) for p in audio_files)
    assert QQuickWindow.grabWindow(window).save(str(reports / "result.png"))
    stages.append("One click -> configured request (browser intercepted) -> byte-identical PPTX -> real voice WAVs + Office preview + mascot")
    sessions = []
    bridge._start_powerpoint_session = lambda *args: sessions.append(args)
    click("useConvertedLessonButton")
    assert window.findChild(QObject, "wholeLessonReview").property("visible")
    click("confirmWholeLessonButton")
    assert len(sessions) == 1 and all(s["approved"] for s in bridge.lesson["segments"])
    stages.append("Draft narration does not approve lesson; explicit whole-deck confirmation hands off to classroom")
    assert not warnings, warnings
    app.exit(0)


QTimer.singleShot(600, safe(accounts))
code = app.exec()
faulthandler.cancel_dump_traceback_later()
if bridge.worker:
    bridge.cancel_event.set()
    bridge.worker.wait()
bridge.browserAI.shutdown()
report = {"status": "passed" if code == 0 and not warnings and not failures else "failed",
          "stages": stages, "warnings": warnings, "failures": failures,
          "scope": "No network uploads; browser conversion intercepted; real selected voice models and Microsoft PowerPoint"}
(reports / "qt-flow.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
window.close()
engine.deleteLater()
app.processEvents()
library.close()
print(json.dumps(report, ensure_ascii=False), flush=True)
raise SystemExit(code)
