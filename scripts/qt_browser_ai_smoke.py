"""Free/Plus account UI and PPTX receive flow; mocked web, real Office preview."""

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
from PySide6.QtCore import QCoreApplication, QEvent, QMetaObject, QObject, Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from app import browser_automation, speech
from app.chatgpt_handoff import load_request
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import RESOURCES, Bridge

Path(".runtime/browser-web-smoke").mkdir(parents=True, exist_ok=True)
workspace = Path(tempfile.mkdtemp(dir=".runtime/browser-web-smoke")).resolve()
reports = Path("reports/browser-web")
reports.mkdir(parents=True, exist_ok=True)
source = workspace / "Nguồn thử.pptx"
deck = Presentation()
slide = deck.slides.add_slide(deck.slide_layouts[6])
slide.shapes.add_textbox(Inches(.5), Inches(.5), Inches(8), Inches(2)).text = "Diện tích · Area"
slide.notes_slide.notes_text_frame.text = "VI: Diện tích bằng 12 cm².\nEN: The area is 12 cm²."
deck.save(source)
attempts, sends, audio, warnings, failures, stages = [], [], [], [], [], []
conversions = []


def fake_login(account, root, cancel, progress, **options):
    attempts.append(account["id"])
    if len(attempts) == 1:
        return {"ready": False}
    if len(attempts) in {2, 4}:
        raise browser_automation.BrowserProblem("verification", browser_automation.VERIFICATION_MESSAGE)
    if len(attempts) == 6:
        assert options["url"] == "https://chatgpt.com/c/fixture" and account["id"] == free_id
    plan = "free" if len(attempts) in {3, 6} else "plus"
    return {"ready": True, "plan": plan, "name": "Cô giáo thử " + plan, "email": plan + "@example.test"}


def fake_convert(account, root, folder, cancel, progress, **options):
    request = load_request(folder)
    assert request["config"]["provider"] == "browser_web"
    assert "FILE POWERPOINT" in request["prompt"] and "VI:" in request["prompt"]
    assert account["plan"] == "free", "Explicit Free testing must win over Plus priority"
    conversions.append(account["id"])
    if len(conversions) == 1:
        sends.append(account["id"])
        browser_automation.write_record(folder, {"account_id": account["id"], "state": "waiting", "followups": 0,
            "url": "https://chatgpt.com/c/fixture", "error": "verification"})
        raise browser_automation.BrowserProblem("verification", browser_automation.VERIFICATION_MESSAGE)
    assert len(sends) == 1 and browser_automation.read_record(folder, account["id"])["state"] == "waiting"
    options["observed"](account["id"], "free", "Web model fixture")
    target = Path(folder) / "bai-giang-song-ngu.pptx"
    target.write_bytes(source.read_bytes())
    browser_automation.write_record(folder, {"account_id": account["id"], "state": "completed", "followups": 0,
        "url": "https://chatgpt.com/c/fixture", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    return {"path": str(target), "url": "https://chatgpt.com/c/fixture"}


browser_automation.login = fake_login
browser_automation.convert = fake_convert
speech.synthesize = lambda text, *_: audio.append(text)
application = QGuiApplication([])
for font in (RESOURCES / "assets").glob("*.ttf"):
    QFontDatabase.addApplicationFontFromData(font.read_bytes())
application.setFont(QFont("Be Vietnam Pro", 10))
QQuickStyle.setStyle("Basic")
library = Library(workspace / "library")
bridge = Bridge(library)
engine = QQmlApplicationEngine()
engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
engine.rootContext().setContextProperty("bridge", bridge)
engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml/Main.qml")))
assert engine.rootObjects(), warnings
window = engine.rootObjects()[0]
window.setProperty("page", "settings")
window.findChild(QObject, "settingsPage").setProperty("activeTab", 6)
phase, deadline, free_id, plus_id, lesson_id = "start", time.monotonic() + 180, "", "", ""


def click(name):
    item = window.findChild(QObject, name)
    assert item and item.property("enabled"), name
    assert QMetaObject.invokeMethod(item, "clicked", Qt.DirectConnection)


def capture(name):
    assert QQuickWindow.grabWindow(window).save(str(reports / name))


def step():
    global phase, free_id, plus_id, lesson_id
    try:
        assert time.monotonic() < deadline, "Web UI flow timed out"
        if phase == "start":
            QMetaObject.invokeMethod(window.findChild(QObject, "helpDialog"), "close", Qt.DirectConnection)
            assert window.findChild(QObject, "browserAccountAdd").property("text") == "Đăng nhập ChatGPT"
            capture("login.png")
            click("browserAccountAdd")
            phase = "closed"
        elif phase == "closed" and not bridge.browserAI.loginBusy:
            assert not bridge.browserAI.accountInfo["ready"]
            assert not window.findChild(QObject, "browserAccountDetails").property("visible")
            assert window.findChild(QObject, "browserConnectionState").property("text") == "Chưa đăng nhập"
            click("browserAccountAdd")
            phase = "verification"
        elif phase == "verification" and not bridge.browserAI.loginBusy:
            assert bridge.browserAI.hasError and bridge.browserAI.verificationBlocked
            assert not bridge.browserAI.accountInfo["ready"]
            assert window.findChild(QObject, "browserManualRecovery").property("visible")
            assert "Cloudflare" in window.findChild(QObject, "browserAccountStatus").property("text")
            assert bridge.browserAI.store.get()["last_error"]["code"] == "verification"
            capture("verification-blocked.png")
            # The fallback is an explicit choice and must not claim a connection.
            click("browserManualRecovery")
            assert not bridge.browserAI.automatic and not bridge.browserAI.accountInfo["ready"]
            assert window.property("page") == "new"
            bridge.browserAI.saveOptions(True, True)
            window.setProperty("page", "settings")
            window.findChild(QObject, "settingsPage").setProperty("activeTab", 6)
            stages.append("Verification error persisted; explicit manual fallback does not mark an account ready")
            click("browserAccountAdd")
            phase = "free"
        elif phase == "free" and not bridge.browserAI.loginBusy:
            assert bridge.browserAI.accountInfo["ready"] and bridge.browserAI.accountInfo["plan"] == "free"
            assert len(bridge.browserAI.accounts) == 1 and attempts[0] == attempts[1] == attempts[2]
            assert not bridge.browserAI.verificationBlocked and "last_error" not in bridge.browserAI.store.get()
            free_id = bridge.browserAI.activeId
            assert window.findChild(QObject, "browserAccountAdd").property("text") == "Thêm tài khoản"
            assert "số dư" in window.findChild(QObject, "browserQuotaStatus").property("text")
            capture("free-connected.png")
            stages.append("One login button; closed window is not success; successful Free session saved")
            click("browserAccountAdd")
            phase = "plus_failed"
        elif phase == "plus_failed" and not bridge.browserAI.loginBusy:
            assert len(bridge.browserAI.accounts) == 2 and not bridge.browserAI.accountInfo["ready"]
            assert bridge.browserAI.activeId != free_id and bridge.browserAI.store.preferred()["id"] == free_id
            assert window.findChild(QObject, "browserAccountAdd").property("text") == "Đăng nhập ChatGPT"
            click("browserAccountAdd")
            phase = "plus"
        elif phase == "plus" and not bridge.browserAI.loginBusy:
            assert len(bridge.browserAI.accounts) == 2 and bridge.browserAI.accountInfo["plan"] == "plus"
            assert attempts[3] == attempts[4], "Retry must reopen the failed new account, not add/reopen a different profile"
            plus_id = bridge.browserAI.activeId
            assert free_id != plus_id
            capture("plus-preferred.png")
            bridge.browserAI.select(free_id)
            assert not bridge.browserAI.autoSelection
            assert "Cố định" in window.findChild(QObject, "browserSelectionPolicy").property("text")
            capture("free-pinned.png")
            stages.append("Adding Plus preserves Free; automatic Plus priority; explicit Free test selection")
            bridge.convertBrowserAI("Bài thử", "Toán", "THPT", "11", "", QUrl.fromLocalFile(str(source)).toString(),
                                    2, "split_view", "standard", "source", "level")
            phase = "blocked_conversion"
        elif phase == "blocked_conversion" and not bridge.busy:
            assert bridge.error and bridge.browserState["needsLogin"]
            assert not bridge.browserAI.store.get(free_id)["ready"]
            assert window.findChild(QObject, "browserConversionResume").property("text") == "Đăng nhập và tiếp tục"
            reopened = Bridge(library)
            assert reopened.browserState["needsLogin"] and reopened.chatgptRequest["folder"] == bridge.chatgptRequest["folder"]
            reopened.browserAI.shutdown()
            reopened.deleteLater()
            capture("conversion-reconnect.png")
            click("browserConversionResume")
            stages.append("Failed new account retries its own profile; conversion verification clears stale ready state and reconnects its pinned account")
            phase = "converted"
        elif phase == "converted" and not bridge.busy and not bridge.browserAI.loginBusy and len(conversions) == 2:
            assert not bridge.error, bridge.message
            assert sends == [free_id]
            assert bridge.lesson["external_deck"] and bridge.quickResult["image"]
            assert Path(bridge.quickResult["path"]).read_bytes() == source.read_bytes()
            assert not any(segment["approved"] for segment in bridge.lesson["segments"])
            if bridge.voiceSettings["en"]:
                assert audio, "Requested narration must be prepared"
            assert window.property("page") == "result"
            lesson_id = bridge.lesson["id"]
            capture("result.png")
            bridge.browserAI.preferPaid()
            assert bridge.browserAI.store.preferred()["id"] == plus_id
            assert bridge.browserAI.conversionAccount(bridge.chatgptRequest["folder"])["id"] == free_id
            bridge.browserAI.remove(free_id)
            bridge.browserAI.remove(plus_id)
            bridge.runBrowserAI()
            phase = "cached"
        elif phase == "cached" and not bridge.busy:
            assert not bridge.error and bridge.lesson["id"] == lesson_id
            assert len(sends) == 1 and not bridge.browserAI.accounts
            stages.append("PPTX/narration received; Office preview rendered; teacher approval kept; cached lesson opens without accounts/resend")
            application.quit()
            return
    except Exception:
        failures.append(traceback.format_exc())
        print(failures[-1], flush=True)
        application.exit(1)
        return
    QTimer.singleShot(100, step)


QTimer.singleShot(250, step)
code = application.exec()
# Destroy QML while its Python bridge is still alive, including queued job
# cleanup; otherwise interpreter teardown can evaluate properties too late.
engine.deleteLater()
QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
bridge.browserAI.shutdown()
library.close()
result = {"status": "passed" if not failures and not warnings else "failed", "stages": stages,
          "warnings": warnings, "failures": failures, "scope": "Fixture web login/conversion; real Qt/Office preview; no real ChatGPT request"}
(reports / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False), flush=True)
sys.exit(code or bool(failures) or bool(warnings))
