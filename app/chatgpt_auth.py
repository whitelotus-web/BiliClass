"""Official local ChatGPT OAuth. Credentials never enter lesson data or logs."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from contextlib import ExitStack
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Event
from urllib.parse import parse_qs, urlencode, urlsplit
from uuid import UUID, uuid4

import httpx
import jwt

from .browser_accounts import profile_lock
from .login_browser import LoginBrowserError, PrivateLoginBrowser

ISSUER = "https://auth.openai.com"
RESOURCE = "https://api.openai.com/v1"
SCOPE = "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct"
PLAN_SCOPE = "chatgpt.tokens.use.direct"
USAGE_URL = "https://chatgpt.com/#settings/Usage"


class PlanError(ValueError):
    def __init__(self, message, code="", status=0):
        super().__init__(message)
        self.code, self.status = code, status


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(str(uuid4()) + ".tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class WindowsSecrets:
    """Windows user-bound DPAPI; no plaintext or portable fallback."""

    def __init__(self, root):
        self.root = Path(root)

    def path(self, account_id):
        if str(UUID(account_id)) != account_id:
            raise ValueError("Mã kết nối không hợp lệ.")
        return self.root / (account_id + ".dpapi")

    def write(self, account_id, value):
        if os.name != "nt":
            raise PlanError("Lưu kết nối ChatGPT hiện cần cơ chế bảo vệ tài khoản Windows.")
        import win32crypt

        raw = json.dumps(value).encode()
        encrypted = win32crypt.CryptProtectData(raw, "BiliClass ChatGPT", None, None, None, 1)
        target = self.path(account_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(str(uuid4()) + ".tmp")
        try:
            temporary.write_bytes(encrypted)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)

    def read(self, account_id):
        if os.name != "nt":
            raise PlanError("Không đọc được kết nối ChatGPT trên hệ điều hành này.")
        import win32crypt

        try:
            encrypted = self.path(account_id).read_bytes()
            return json.loads(win32crypt.CryptUnprotectData(encrypted, None, None, None, 1)[1])
        except Exception:
            raise PlanError("Kết nối đã mất hoặc không thuộc tài khoản Windows này. Đăng nhập lại.") from None

    def remove(self, account_id):
        self.path(account_id).unlink(missing_ok=True)


class PlanAccounts:
    def __init__(self, directory, secret_store=None):
        self.root = (Path(directory) / "chatgpt_plan").resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "accounts.json"
        self.secrets = secret_store or WindowsSecrets(self.root / "credentials")
        self.reload()
        host_path = self.root / "host.json"
        if not host_path.exists():
            atomic_json(host_path, {"ext_agent_host_id": "urn:uuid:" + str(uuid4())})
        self.host_id = json.loads(host_path.read_text(encoding="utf-8"))["ext_agent_host_id"]
        if not self.host_id.startswith("urn:uuid:") or str(UUID(self.host_id[9:])) != self.host_id[9:]:
            raise PlanError("Định danh máy ChatGPT không hợp lệ.")

    def reload(self):
        self.data = {"version": 1, "accounts": [], "active": "", "automatic": True, "audio": True}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data.get("version") != 1 or not isinstance(data.get("accounts"), list):
                raise PlanError("Danh sách kết nối ChatGPT không hợp lệ.")
            for item in data["accounts"]:
                if str(UUID(item["id"])) != item["id"]:
                    raise PlanError("Mã kết nối ChatGPT không hợp lệ.")
            self.data.update(data)

    def save(self):
        atomic_json(self.path, self.data)

    def get(self, account_id=None):
        selected = self.data["active"] if account_id is None else account_id
        item = next((a for a in self.data["accounts"] if a["id"] == selected), None)
        if item is None:
            raise PlanError("Đăng nhập trong Cài đặt → Browser AI trước khi chuyển đổi.", "sign_in_required")
        return dict(item)

    def preferred(self):
        # The teacher's selection wins. Never rotate accounts to avoid quotas.
        return self.get()

    def select(self, account_id):
        self.get(account_id)
        self.data["active"] = account_id
        self.save()

    def options(self, automatic, audio):
        self.data.update(automatic=bool(automatic), audio=bool(audio))
        self.save()

    def registration(self, account_id=""):
        if account_id:
            return self.get(account_id)
        pending = self.root / "pending-registration.json"
        if pending.is_file():
            return json.loads(pending.read_text(encoding="utf-8"))
        return {"client_id": "dynamic_agent_client"}

    def save_registration(self, client_id):
        # Keep the issued ID even if exchange fails; it is not a credential.
        atomic_json(self.root / "pending-registration.json", {"client_id": client_id})

    def connect(self, claims, tokens, client_id, account_id=""):
        if account_id and self.get(account_id)["sub"] != claims["sub"]:
            raise PlanError("Bạn vừa đăng nhập tài khoản khác. Dùng Thêm tài khoản để lưu riêng.")
        account_id = account_id or next((a["id"] for a in self.data["accounts"]
                                         if a["sub"] == claims["sub"] and a["client_id"] == client_id), str(uuid4()))
        self.secrets.write(account_id, tokens)
        email = str(claims.get("email") or claims.get("name") or "Tài khoản ChatGPT")[:200]
        enabled = PLAN_SCOPE in tokens.get("scope", "").split()
        item = {"id": account_id, "client_id": client_id, "sub": claims["sub"], "label": email,
                "ready": enabled, "status": "Đã kết nối · Dùng hạn mức ChatGPT" if enabled else
                "Đã đăng nhập · Chưa cấp quyền xử lý", "plan": "", "provider": "chatgpt_plan"}
        self.data["accounts"] = [a for a in self.data["accounts"] if a["id"] != account_id] + [item]
        self.data["active"] = account_id
        self.save()
        (self.root / "pending-registration.json").unlink(missing_ok=True)
        return item

    def remove_local(self, account_id):
        self.get(account_id)
        self.secrets.remove(account_id)
        self.data["accounts"] = [a for a in self.data["accounts"] if a["id"] != account_id]
        if self.data["active"] == account_id:
            self.data["active"] = self.data["accounts"][0]["id"] if self.data["accounts"] else ""
        self.save()


def response_error(response):
    """Public diagnostics only; do not surface response bodies containing tokens."""
    try:
        body = response.json()
        error = body.get("error", {})
        code = error.get("code", "") if isinstance(error, dict) else str(error)
    except Exception:
        code = ""
    messages = {
        "subscription_sharing_user_not_eligible": "Tài khoản hoặc ứng dụng chưa được cấp quyền dùng hạn mức ChatGPT. Có thể chọn gửi/nhận thủ công.",
        "subscription_sharing_usage_limit_exceeded": "Đã đạt hạn mức ChatGPT cho yêu cầu này. Xem hạn mức; bài đã xử lý được giữ lại.",
        "subscription_sharing_usage_unavailable": "Chưa kiểm tra được hạn mức ChatGPT. Giữ yêu cầu và thử lại sau.",
        "subscription_sharing_unsupported_capability": "Model/kết nối chưa hỗ trợ cấu hình xử lý này. Chọn model phù hợp hoặc gửi/nhận thủ công.",
        "subscription_sharing_route_not_supported": "Kết nối ChatGPT chưa cho phép đường xử lý này.",
        "invalid_grant": "Phiên ChatGPT hoặc mã đăng nhập đã hết hạn. Đăng nhập lại.",
        "access_denied": "Bạn chưa đồng ý cấp quyền kết nối ChatGPT.",
    }
    message = messages.get(code, {
        401: "Phiên ChatGPT không được chấp nhận. Đăng nhập lại.",
        403: "ChatGPT chưa cho phép kết nối này. Kiểm tra quyền ứng dụng/tài khoản hoặc dùng cách gửi thủ công.",
        429: "Đã đạt hạn mức ChatGPT. Xem hạn mức và thử lại sau.",
        503: "Kết nối ChatGPT tạm chưa khả dụng. Bài đang làm được giữ lại.",
    }.get(response.status_code, f"Kết nối ChatGPT thất bại (HTTP {response.status_code})."))
    return PlanError(message, code, response.status_code)


class ChatGPTAuth:
    def __init__(self, accounts, client=None):
        self.accounts = accounts
        self.client = client or httpx.Client(timeout=httpx.Timeout(30, connect=10), follow_redirects=False)
        self._metadata = None

    def metadata(self):
        if self._metadata is None:
            response = self.client.get(ISSUER + "/.well-known/openid-configuration")
            if response.status_code != 200:
                raise response_error(response)
            value = response.json()
            if value.get("issuer") != ISSUER:
                raise PlanError("Địa chỉ xác thực ChatGPT không hợp lệ.")
            for field in ("authorization_endpoint", "token_endpoint", "jwks_uri", "revocation_endpoint"):
                if field == "revocation_endpoint" and not value.get(field):
                    continue
                parsed = urlsplit(value.get(field, ""))
                if parsed.scheme != "https" or parsed.netloc != "auth.openai.com" or parsed.fragment:
                    raise PlanError("Địa chỉ xác thực ChatGPT không hợp lệ.")
            self._metadata = value
        return self._metadata

    def verify_identity(self, encoded, client_id, nonce=None):
        metadata = self.metadata()
        try:
            header = jwt.get_unverified_header(encoded)
            if header.get("alg") != "RS256" or not header.get("kid"):
                raise ValueError()
            response = self.client.get(metadata["jwks_uri"])
            if response.status_code != 200:
                raise ValueError()
            key = next(k for k in response.json()["keys"] if k.get("kid") == header["kid"])
            claims = jwt.decode(encoded, jwt.PyJWK(key).key, algorithms=["RS256"], audience=client_id,
                                issuer=ISSUER, options={"require": ["exp", "iat", "sub", "iss", "aud"]})
            if not isinstance(claims["sub"], str) or not claims["sub"]:
                raise ValueError()
            if nonce is not None and not hmac.compare_digest(str(claims.get("nonce", "")), nonce):
                raise ValueError()
            return claims
        except Exception:
            raise PlanError("Không xác minh được danh tính ChatGPT. Hủy kết nối này và đăng nhập lại.") from None

    def token_exchange(self, form, previous=None):
        response = self.client.post(self.metadata()["token_endpoint"], data=form)
        if response.status_code != 200:
            raise response_error(response)
        data = response.json()
        expires = data.get("expires_in")
        if not isinstance(data.get("access_token"), str) or not data["access_token"] or type(expires) is not int or expires <= 0:
            raise PlanError("ChatGPT chưa trả phiên hợp lệ. Đăng nhập lại.")
        result = {key: data.get(key, (previous or {}).get(key, ""))
                  for key in ("access_token", "refresh_token", "id_token", "scope")}
        result["expires_at"] = time.time() + expires
        return result

    def authorize(self, account_id="", cancel=None, progress=lambda _: None, opener=None, timeout=600):
        cancel = cancel or Event()
        registration = self.accounts.registration(account_id)
        client_id = registration["client_id"]
        state, nonce, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(32), secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
        returned = {}

        class Callback(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass  # Never print an authorization code or query string.

            def do_GET(self):
                url = urlsplit(self.path)
                query = parse_qs(url.query, keep_blank_values=True)
                valid = (url.path == "/auth/callback" and len(query.get("state", [])) == 1
                         and hmac.compare_digest(query["state"][0], state)
                         and not returned and all(len(query.get(k, [])) <= 1 for k in ("code", "error", "client_id")))
                if valid and (query.get("code", [""])[0] or query.get("error", [""])[0]):
                    returned.update({k: values[0] for k, values in query.items()})
                    status, text = 200, "BiliClass: da nhan dang nhap. Ban co the quay lai ung dung."
                else:
                    status, text = 400, "Callback khong hop le. Quay lai BiliClass de dang nhap."
                body = text.encode()
                self.send_response(status)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

        server = HTTPServer(("127.0.0.1", 0), Callback)
        server.timeout = .3
        redirect = f"http://127.0.0.1:{server.server_port}/auth/callback"
        params = {"client_id": client_id, "ext_agent_host_id": self.accounts.host_id,
                  "response_type": "code", "redirect_uri": redirect, "scope": SCOPE, "resource": RESOURCE,
                  "state": state, "nonce": nonce, "code_challenge": challenge, "code_challenge_method": "S256"}
        if client_id == "dynamic_agent_client":
            params["agent_name_hint"] = "BiliClass"
        if account_id:
            params["login_hint"] = registration["label"]
            try:
                previous = self.accounts.secrets.read(account_id)
            except PlanError:
                previous = {}
            if previous.get("id_token"):
                params["id_token_hint"] = previous["id_token"]
        lifetime = ExitStack()
        try:
            url = self.metadata()["authorization_endpoint"] + "?" + urlencode(params)
            browser = None
            if opener is None:
                browser = lifetime.enter_context(PrivateLoginBrowser(self.accounts))
                opener = browser.open
            if not opener(url):
                raise PlanError("Chưa mở được phiên đăng nhập ChatGPT.")
            progress("Đăng nhập trong cửa sổ riêng của BiliClass và cho phép dùng hạn mức ChatGPT. Cửa sổ tự đóng khi xong…")
            deadline = time.monotonic() + timeout
            while not returned:
                if cancel.is_set():
                    raise PlanError("Đã hủy đăng nhập.", "cancelled")
                if time.monotonic() >= deadline:
                    raise PlanError("Hết thời gian chờ đăng nhập. Nếu trang báo lỗi, ghi lại thông báo rồi đăng nhập lại hoặc dùng gửi/nhận thủ công.", "login_timeout")
                if browser and not browser.running():
                    raise PlanError("Cửa sổ đăng nhập đã đóng trước khi kết nối xong. Bấm Continue with ChatGPT để mở lại.", "browser_closed")
                server.handle_request()
        except LoginBrowserError as exc:
            raise PlanError(str(exc), "login_browser") from None
        finally:
            server.server_close()
            lifetime.close()
        if cancel.is_set():
            raise PlanError("Đã hủy đăng nhập.", "cancelled")
        if returned.get("error"):
            code = returned["error"]
            messages = {
                "access_denied": "Bạn chưa đồng ý cấp quyền kết nối ChatGPT.",
                "invalid_client": "ChatGPT chưa chấp nhận đăng ký ứng dụng BiliClass. Có thể dùng gửi/nhận thủ công.",
                "subscription_sharing_user_not_eligible": "Tài khoản hoặc ứng dụng chưa đủ điều kiện dùng hạn mức ChatGPT. Có thể dùng gửi/nhận thủ công.",
                "invalid_scope": "ChatGPT chưa chấp nhận quyền kết nối được yêu cầu. Có thể dùng gửi/nhận thủ công.",
            }
            raise PlanError(messages.get(code, "ChatGPT chưa cho phép kết nối này. Thử lại hoặc dùng gửi/nhận thủ công."),
                            code if code in messages else "authorization_failed")
        issued = returned.get("client_id") or (client_id if client_id != "dynamic_agent_client" else "")
        if not issued or issued == "dynamic_agent_client" or (client_id != "dynamic_agent_client" and issued != client_id):
            raise PlanError("ChatGPT chưa cấp mã đăng ký hợp lệ cho BiliClass.")
        if not account_id:
            self.accounts.save_registration(issued)
        tokens = self.token_exchange({"grant_type": "authorization_code", "client_id": issued, "code": returned["code"],
                                      "code_verifier": verifier, "redirect_uri": redirect, "resource": RESOURCE})
        claims = self.verify_identity(tokens["id_token"], issued, nonce)
        return self.accounts.connect(claims, tokens, issued, account_id)

    def access_token(self, account_id):
        with profile_lock(self.accounts.root, account_id):
            self.accounts.reload()
            account = self.accounts.get(account_id)
            tokens = self.accounts.secrets.read(account_id)
            if PLAN_SCOPE not in tokens.get("scope", "").split():
                raise PlanError("Chưa cấp quyền dùng hạn mức ChatGPT. Đăng nhập lại và cho phép xử lý bài.", "plan_permission_missing")
            if tokens.get("expires_at", 0) < time.time() + 90:
                if not tokens.get("refresh_token"):
                    raise PlanError("Phiên ChatGPT đã hết hạn. Đăng nhập lại.", "sign_in_required")
                fresh = self.token_exchange({"grant_type": "refresh_token", "client_id": account["client_id"],
                                             "refresh_token": tokens["refresh_token"], "resource": RESOURCE}, tokens)
                if fresh.get("id_token") and fresh["id_token"] != tokens.get("id_token"):
                    if self.verify_identity(fresh["id_token"], account["client_id"])["sub"] != account["sub"]:
                        raise PlanError("Danh tính ChatGPT đã thay đổi. Đăng nhập lại.")
                self.accounts.secrets.write(account_id, fresh)
                tokens = fresh
                if PLAN_SCOPE not in tokens.get("scope", "").split():
                    raise PlanError("Quyền dùng hạn mức ChatGPT đã bị thu hồi. Đăng nhập lại.", "plan_permission_missing")
            return tokens["access_token"]

    def disconnect(self, account_id):
        confirmed = False
        with profile_lock(self.accounts.root, account_id):
            account = self.accounts.get(account_id)
            try:
                tokens = self.accounts.secrets.read(account_id)
                endpoint = self.metadata().get("revocation_endpoint")
                if endpoint and tokens.get("refresh_token"):
                    response = self.client.post(endpoint, data={"token": tokens["refresh_token"],
                                                "token_type_hint": "refresh_token", "client_id": account["client_id"]})
                    confirmed = response.status_code == 200
            except Exception:
                pass
            self.accounts.remove_local(account_id)
        return confirmed
