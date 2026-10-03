"""Qt login failure/recovery controls; no browser or real account is used."""

import json
import sys
import tempfile
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx
from PySide6.QtCore import QMetaObject, QObject, Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from app import browser_ai_ui
from app.chatgpt_auth import LOGIN_SESSION_MESSAGE, PLAN_SCOPE, WORKSPACE_DENIED_MESSAGE, PlanError
from app.library import Library
from app.paths import RESOURCE_ROOT
from app.ui import RESOURCES, Bridge

Path('.runtime/chatgpt-login-smoke').mkdir(parents=True, exist_ok=True)
workspace = Path(tempfile.mkdtemp(dir='.runtime/chatgpt-login-smoke')).resolve()
attempts, stages, failures, warnings = [], [], [], []
folder = Path('reports/chatgpt-plan')
folder.mkdir(parents=True, exist_ok=True)


class FixtureAuth:
    def __init__(self, store):
        self.accounts = store
        self.client = httpx.Client()

    def authorize(self, account_id, _cancel, progress, *, resume_pending=False):
        attempts.append((account_id, resume_pending))
        progress('Đang kiểm tra kết nối thử…')
        if len(attempts) == 1:
            raise PlanError(WORKSPACE_DENIED_MESSAGE, '3p_login_workspace_scope_denied')
        if len(attempts) == 2:
            raise PlanError(LOGIN_SESSION_MESSAGE, 'browser_authentication_error')
        if len(attempts) == 3:
            self.accounts.save_registration('oaiapp_fixture')
            raise PlanError('Mã đăng nhập đã hết hạn. Đăng nhập lại.', 'invalid_grant')
        if len(attempts) == 6:
            assert _cancel.wait(5), 'Single button did not cancel sign-in'
            raise PlanError('Đã hủy đăng nhập.', 'cancelled')
        return self.accounts.connect({'sub': 'fixture', 'name': 'Cô giáo thử nghiệm', 'email': 'teacher@example.test'},
                                     {'scope': PLAN_SCOPE}, 'oaiapp_fixture', account_id)


browser_ai_ui.ChatGPTAuth = FixtureAuth
application = QGuiApplication([])
for font in (RESOURCES / 'assets').glob('*.ttf'):
    QFontDatabase.addApplicationFontFromData(font.read_bytes())
application.setFont(QFont('Be Vietnam Pro', 10))
QQuickStyle.setStyle('Basic')
library = Library(workspace / 'library')
bridge = Bridge(library)
bridge.browserAI.store.save_registration('oaiapp_fixture')
bridge.browserAI.store.data['last_error'] = {'code': 'browser_closed', 'message': 'Cửa sổ đã đóng trước khi kết nối xong.'}
bridge.browserAI.store.save()
bridge.browserAI.inform(bridge.browserAI.store.data['last_error']['message'])
engine = QQmlApplicationEngine()
engine.warnings.connect(lambda values: warnings.extend(map(str, values)))
engine.rootContext().setContextProperty('bridge', bridge)
engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / 'qml/Main.qml')))
assert engine.rootObjects(), warnings
window = engine.rootObjects()[0]
window.setProperty('page', 'settings')
window.findChild(QObject, 'settingsPage').setProperty('activeTab', 6)
deadline, phase = time.monotonic() + 30, 'start'


def click_login():
    button = window.findChild(QObject, 'browserAccountAdd')
    assert button.property('enabled')
    assert QMetaObject.invokeMethod(button, 'clicked', Qt.DirectConnection)
    assert bridge.browserAI.loginBusy and not bridge.browserAI.hasError
    assert button.property('text') == 'Hủy'


def capture(name):
    assert QQuickWindow.grabWindow(window).save(str(folder / name))


def step():
    global phase
    try:
        assert time.monotonic() < deadline, 'Qt login recovery timed out'
        if phase == 'start':
            assert window.findChild(QObject, 'browserAccountAdd').property('text') == 'Đăng nhập ChatGPT'
            assert window.findChild(QObject, 'browserResumeLogin') is None
            assert window.findChild(QObject, 'browserLoginStop') is None
            assert not window.findChild(QObject, 'browserAccountMenu').property('visible')
            capture('login-simple.png')
            click_login()
            phase = 'denied'
        elif phase == 'denied' and not bridge.browserAI.loginBusy:
            assert bridge.browserAI.message == WORKSPACE_DENIED_MESSAGE
            assert not bridge.browserAI.accounts and bridge.browserAI.canResume
            assert bridge.browserAI.hasError and not bridge.browserAI.accountInfo
            assert window.findChild(QObject, 'browserAccountAdd').property('enabled')
            bridge.browserAI.store.reload()
            assert bridge.browserAI.store.data['last_error']['code'] == '3p_login_workspace_scope_denied'
            capture('login-denied.png')
            stages.append('Closed browser and workspace rejection start fresh; failure shows no saved identity')
            click_login()
            phase = 'session_failed'
        elif phase == 'session_failed' and not bridge.browserAI.loginBusy:
            assert bridge.browserAI.store.data['last_error']['code'] == 'browser_authentication_error'
            assert bridge.browserAI.hasError and not bridge.browserAI.accountInfo
            assert bridge.browserAI.message == LOGIN_SESSION_MESSAGE
            stages.append('Authentication error ends waiting, preserves the one login action and shows a fresh-session recovery')
            click_login()
            phase = 'exchange_failed'
        elif phase == 'exchange_failed' and not bridge.browserAI.loginBusy:
            assert bridge.browserAI.hasError and not bridge.browserAI.accountInfo
            assert bridge.browserAI.store.data['last_error']['code'] == 'invalid_grant'
            click_login()
            phase = 'connected'
        elif phase == 'connected' and not bridge.browserAI.loginBusy:
            assert len(bridge.browserAI.accounts) == 1 and bridge.browserAI.store.get()['ready']
            assert attempts == [('', False), ('', False), ('', False), ('', True)]
            assert not bridge.browserAI.canResume and not bridge.browserAI.store.data['last_error']
            assert not bridge.browserAI.hasError
            assert bridge.browserAI.accountInfo['name'] == 'Cô giáo thử nghiệm'
            assert bridge.browserAI.accountInfo['email'] == 'teacher@example.test'
            assert bridge.browserAI.accountInfo['saved'] and not bridge.browserAI.accountInfo['plan']
            assert window.findChild(QObject, 'browserAccountIdentity').property('text') == 'Cô giáo thử nghiệm'
            assert window.findChild(QObject, 'browserAccountMenu').property('visible')
            assert window.findChild(QObject, 'browserStoredAccountsMenu').property('count') == 1
            assert window.findChild(QObject, 'browserAccountAdd').property('text') == 'Đăng nhập lại'
            assert 'Chưa có số liệu' in window.findChild(QObject, 'browserQuotaStatus').property('text')
            capture('login-connected.png')
            stages.append('Interrupted exchange resumes through the same action; verified identity/date/quota fallback shown inline')
            window.setWidth(1080)
            window.setHeight(700)
            phase = 'compact'
        elif phase == 'compact':
            capture('login-connected-compact.png')
            click_login()
            phase = 'reauthorized'
        elif phase == 'reauthorized' and not bridge.browserAI.loginBusy:
            assert len(bridge.browserAI.accounts) == 1
            assert attempts[-1] == (bridge.browserAI.activeId, False)
            stages.append('Saved connection reauthorization retains account/client mapping and uses the same button')
            click_login()
            assert QMetaObject.invokeMethod(window.findChild(QObject, 'browserAccountAdd'), 'clicked', Qt.DirectConnection)
            phase = 'cancelled'
        elif phase == 'cancelled' and not bridge.browserAI.loginBusy:
            assert not bridge.browserAI.hasError and len(bridge.browserAI.accounts) == 1
            assert bridge.browserAI.store.get()['ready']
            stages.append('Same button cancels sign-in without deleting the saved connection')
            application.exit(0)
            return
    except Exception:
        failures.append(traceback.format_exc())
        application.exit(1)
        return
    QTimer.singleShot(100, step)


QTimer.singleShot(1000, step)
status = application.exec()
window.hide()
del engine
bridge.browserAI.shutdown()
library.close()
report = {'status': 'passed' if status == 0 and not failures and not warnings else 'failed',
          'stages': stages, 'warnings': warnings, 'failures': failures,
          'scope': 'Qt controls with fixture OAuth; no real sign-in, browser or inference'}
(folder / 'qt-login.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False), flush=True)
raise SystemExit(0 if report['status'] == 'passed' else 1)
