import json
import threading
import time
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.chatgpt_auth import ISSUER, PLAN_SCOPE, ChatGPTAuth, PlanAccounts, PlanError, WindowsSecrets


class MemorySecrets:
    def __init__(self):
        self.values = {}

    def write(self, key, value):
        self.values[key] = dict(value)

    def read(self, key):
        return dict(self.values[key])

    def remove(self, key):
        self.values.pop(key, None)


@pytest.fixture
def service(tmp_path):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key()))
    public.update(kid="key1", alg="RS256", use="sig")
    accounts = PlanAccounts(tmp_path, MemorySecrets())
    requests, exchange = [], {}

    def signed(sub="teacher", aud="oaiapp_test", **kwargs):
        claims = {"sub": sub, "aud": aud, "iss": ISSUER, "iat": int(time.time()),
                  "exp": int(time.time()) + 3600, "email": "teacher@example.test", **kwargs}
        return jwt.encode(claims, private, algorithm="RS256", headers={"kid": "key1"})

    def route(request):
        requests.append(request)
        if request.url.path.endswith("openid-configuration"):
            return httpx.Response(200, json={"issuer": ISSUER, "authorization_endpoint": ISSUER + "/authorize",
                "token_endpoint": ISSUER + "/token", "jwks_uri": ISSUER + "/jwks", "revocation_endpoint": ISSUER + "/revoke"})
        if request.url.path == "/jwks":
            return httpx.Response(200, json={"keys": [public]})
        if request.url.path == "/token":
            return httpx.Response(200, json={"access_token": "access-test", "refresh_token": "refresh-new",
                "id_token": signed(nonce=exchange.get("nonce", "")), "expires_in": 3600, "scope": exchange.get("scope", PLAN_SCOPE)})
        if request.url.path == "/revoke":
            return httpx.Response(200)
        raise AssertionError(request.url)

    auth = ChatGPTAuth(accounts, httpx.Client(transport=httpx.MockTransport(route)))
    return auth, accounts, signed, exchange, requests


def test_oauth_callback_registration_pkce_and_scope(service):
    auth, accounts, _signed, exchange, requests = service
    threads = []

    def opener(url):
        values = parse_qs(urlsplit(url).query)
        assert values["client_id"] == ["dynamic_agent_client"]
        assert values["agent_name_hint"] == ["BiliClass"]
        assert values["ext_agent_host_id"] == [accounts.host_id]
        exchange["nonce"] = values["nonce"][0]
        callback = values["redirect_uri"][0]

        def respond():
            bad = httpx.get(callback + "?" + urlencode({"state": "wrong", "code": "evil"}))
            assert bad.status_code == 400
            good = httpx.get(callback + "?" + urlencode({"state": values["state"][0], "code": "test-code", "client_id": "oaiapp_test"}))
            assert good.status_code == 200
        thread = threading.Thread(target=respond)
        threads.append(thread)
        thread.start()
        return True

    item = auth.authorize(opener=opener, timeout=5)
    for thread in threads:
        thread.join(5)
    assert item["ready"] and accounts.get()["id"] == item["id"]
    posted = parse_qs(next(r for r in requests if r.url.path == "/token").content.decode())
    assert posted["client_id"] == ["oaiapp_test"]
    assert posted["code_verifier"] and "client_secret" not in posted
    assert "access-test" not in accounts.path.read_text(encoding="utf-8")
    assert "refresh-new" not in accounts.path.read_text(encoding="utf-8")
    assert not (accounts.root / "pending-registration.json").exists()


def test_identity_signature_nonce_audience_and_expiry(service):
    auth, _accounts, signed, _exchange, _requests = service
    assert auth.verify_identity(signed(nonce="ok"), "oaiapp_test", "ok")["sub"] == "teacher"
    for token, audience, nonce in ((signed(nonce="wrong"), "oaiapp_test", "ok"),
                                  (signed(), "oaiapp_other", None), (signed(exp=1), "oaiapp_test", None)):
        with pytest.raises(PlanError, match="danh tính"):
            auth.verify_identity(token, audience, nonce)


def test_reauthorization_uses_issued_client_without_registration_hint(service):
    auth, accounts, signed, exchange, _requests = service
    token = signed()
    original = accounts.connect(auth.verify_identity(token, "oaiapp_test"),
        {"scope": PLAN_SCOPE, "id_token": token}, "oaiapp_test")
    threads = []

    def opener(url):
        values = parse_qs(urlsplit(url).query)
        assert values["client_id"] == ["oaiapp_test"]
        assert "agent_name_hint" not in values
        assert values["id_token_hint"] == [token]
        assert values["login_hint"] == [original["label"]]
        exchange["nonce"] = values["nonce"][0]
        callback = values["redirect_uri"][0] + "?" + urlencode({"state": values["state"][0], "code": "test-code"})
        thread = threading.Thread(target=lambda: httpx.get(callback))
        thread.start()
        threads.append(thread)
        return True

    connected = auth.authorize(original["id"], opener=opener, timeout=5)
    for thread in threads:
        thread.join(5)
    assert connected["id"] == original["id"] and connected["ready"]
    assert len(accounts.data["accounts"]) == 1


def test_new_connection_never_reuses_a_pending_workspace_registration(service):
    auth, accounts, _signed, exchange, requests = service
    accounts.save_registration("oaiapp_other_workspace")
    previous_path = accounts.root / "pending-registration.json"
    previous = previous_path.read_bytes()
    assert accounts.registration()["client_id"] == "dynamic_agent_client"
    assert accounts.registration(resume_pending=True)["client_id"] == "oaiapp_other_workspace"
    assert previous_path.read_bytes() == previous
    threads = []

    def opener(url):
        assert not requests  # No discovery request delays the browser opening.
        values = parse_qs(urlsplit(url).query)
        assert values["client_id"] == ["dynamic_agent_client"]
        assert values["agent_name_hint"] == ["BiliClass"]
        exchange["nonce"] = values["nonce"][0]
        callback = values["redirect_uri"][0] + "?" + urlencode({
            "state": values["state"][0], "code": "test-code", "client_id": "oaiapp_test"})
        thread = threading.Thread(target=lambda: httpx.get(callback))
        thread.start()
        threads.append(thread)
        return True

    item = auth.authorize(opener=opener, timeout=5)
    for thread in threads:
        thread.join(5)
    assert item["ready"] and item["client_id"] == "oaiapp_test"
    assert not previous_path.exists()
    archives = list((accounts.root / "registration-history").glob("*.json"))
    assert len(archives) == 1
    assert json.loads(archives[0].read_text())["client_id"] == "oaiapp_other_workspace"


@pytest.mark.parametrize("kind,final_error,expected_attempts", [
    ("pending", "", 2),
    ("pending", "3p_login_workspace_scope_denied", 2),
    ("pending", "access_denied", 1),
    ("new", "3p_login_workspace_scope_denied", 1),
    ("saved", "3p_login_workspace_scope_denied", 1),
])
def test_workspace_denial_recovers_only_unverified_pending_registration(service, kind, final_error, expected_attempts):
    auth, accounts, signed, exchange, requests = service
    accounts.save_registration("oaiapp_other_workspace")
    account_id = ""
    if kind == "saved":
        token = signed()
        account_id = accounts.connect(auth.verify_identity(token, "oaiapp_test"),
            {"scope": PLAN_SCOPE, "id_token": token}, "oaiapp_test")["id"]
    host_id, before = accounts.host_id, dict(accounts.data)
    attempts, threads = [], []

    def opener(url):
        values = parse_qs(urlsplit(url).query)
        attempts.append(values)
        exchange["nonce"] = values["nonce"][0]
        error = ("3p_login_workspace_scope_denied" if kind == "pending" and len(attempts) == 1
                 and final_error != "access_denied" else final_error)
        result = {"state": values["state"][0]}
        result.update({"error": error} if error else {"code": "new-code", "client_id": "oaiapp_test"})
        callback = values["redirect_uri"][0] + "?" + urlencode(result)
        thread = threading.Thread(target=lambda: httpx.get(callback))
        thread.start()
        threads.append(thread)
        return True

    if final_error:
        with pytest.raises(PlanError) as caught:
            auth.authorize(account_id, opener=opener, timeout=5, resume_pending=kind == "pending")
        assert caught.value.code == final_error
        assert accounts.data == before
        assert not any(r.url.path == "/token" for r in requests)
    else:
        assert auth.authorize(opener=opener, timeout=5, resume_pending=True)["ready"]
    for thread in threads:
        thread.join(5)
    assert len(attempts) == expected_attempts
    assert accounts.host_id == host_id
    if expected_attempts == 2:
        assert attempts[0]["client_id"] == ["oaiapp_other_workspace"]
        assert attempts[1]["client_id"] == ["dynamic_agent_client"]
        assert attempts[1]["agent_name_hint"] == ["BiliClass"]
        assert attempts[0]["ext_agent_host_id"] == attempts[1]["ext_agent_host_id"] == [host_id]
        assert all(attempts[0][k] != attempts[1][k] for k in ("state", "nonce", "code_challenge"))
        record = json.loads((accounts.root / "login-diagnostics.json").read_text(encoding="utf-8"))
        stages = [e["stage"] for e in record["events"]]
        assert stages.count("registration_restarted") == 1
        assert "registration_pending" in stages and "registration_new" in stages


@pytest.mark.parametrize("error", ["invalid_client", "access_denied", "subscription_sharing_user_not_eligible", "3p_login_workspace_scope_denied", "invalid_state"])
def test_authorization_errors_are_reported_without_creating_account(service, error):
    auth, accounts, _signed, _exchange, requests = service
    threads = []

    def opener(url):
        values = parse_qs(urlsplit(url).query)
        callback = values["redirect_uri"][0] + "?" + urlencode({
            "state": values["state"][0], "error": error, "error_description": "DO-NOT-DISPLAY-PRIVATE-DETAILS"})
        thread = threading.Thread(target=lambda: httpx.get(callback))
        thread.start()
        threads.append(thread)
        return True

    with pytest.raises(PlanError) as caught:
        auth.authorize(opener=opener, timeout=5)
    for thread in threads:
        thread.join(5)
    assert caught.value.code == error
    assert "DO-NOT-DISPLAY" not in str(caught.value)
    assert not accounts.data["accounts"] and not any(r.url.path == "/token" for r in requests)


@pytest.mark.parametrize("reason", ["closed", "cancelled", "workspace_denied", "loading", "authentication_error"])
def test_owned_login_browser_cleanup_when_closed_or_cancelled(service, monkeypatch, reason):
    from app import chatgpt_auth

    auth, accounts, _signed, _exchange, _requests = service
    cancel = threading.Event()
    events = []
    monkeypatch.setattr(chatgpt_auth, "LOGIN_PAGE_TIMEOUT", .01)

    class Browser:
        def __init__(self, store):
            assert store is accounts

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            events.append("closed")

        def open(self, _url):
            events.append("opened")
            if reason == "cancelled":
                cancel.set()
            return True

        def running(self):
            return reason != "closed"

        def status(self):
            return reason

    monkeypatch.setattr(chatgpt_auth, "PrivateLoginBrowser", Browser)
    with pytest.raises(PlanError) as caught:
        auth.authorize(cancel=cancel, timeout=5)
    expected = {"closed": "browser_closed", "cancelled": "cancelled",
                "workspace_denied": "3p_login_workspace_scope_denied", "loading": "login_page_timeout",
                "authentication_error": "browser_authentication_error"}
    assert caught.value.code == expected[reason]
    assert events == ["opened", "closed"] and not accounts.data["accounts"]


@pytest.mark.parametrize("outcome", ["success", "exchange_rejected", "cancel_during_exchange"])
def test_browser_and_profile_lock_survive_exchange_and_identity_validation(service, monkeypatch, outcome):
    from app import chatgpt_auth
    from app.browser_accounts import ProfileBusy, profile_lock

    auth, accounts, _signed, exchange, _requests = service
    cancel = threading.Event()
    flags, threads = {"open": False, "closed": False}, []
    original = auth.client

    def route(request):
        assert flags["open"] and not flags["closed"]
        with pytest.raises(ProfileBusy):
            with profile_lock(accounts.root / "browser-lock", accounts.host_id[9:]):
                pass
        if request.url.path == "/token":
            if outcome == "exchange_rejected":
                return httpx.Response(400, json={"error": {"code": "invalid_grant", "message": "DO-NOT-LOG"}},
                                      headers={"x-request-id": "req_test_rejected"})
            if outcome == "cancel_during_exchange":
                cancel.set()
        return original._transport.handle_request(request)

    auth.client = httpx.Client(transport=httpx.MockTransport(route))

    class Browser:
        def __init__(self, store):
            assert store is accounts

        def __enter__(self):
            self.lock = profile_lock(accounts.root / "browser-lock", accounts.host_id[9:])
            self.lock.__enter__()
            return self

        def __exit__(self, *args):
            flags["closed"] = True
            self.lock.__exit__(*args)

        def open(self, url):
            flags["open"] = True
            values = parse_qs(urlsplit(url).query)
            exchange["nonce"] = values["nonce"][0]
            callback = values["redirect_uri"][0] + "?" + urlencode({
                "state": values["state"][0], "code": "test-code", "client_id": "oaiapp_test"})
            thread = threading.Thread(target=lambda: httpx.get(callback))
            thread.start()
            threads.append(thread)
            return True

        def running(self):
            return not flags["closed"]

        def status(self):
            return "waiting"

    monkeypatch.setattr(chatgpt_auth, "PrivateLoginBrowser", Browser)
    if outcome == "success":
        assert auth.authorize(cancel=cancel, timeout=5)["ready"]
    else:
        with pytest.raises(PlanError) as caught:
            auth.authorize(cancel=cancel, timeout=5)
        assert caught.value.code == ("invalid_grant" if outcome == "exchange_rejected" else "cancelled")
        assert not accounts.data["accounts"]
    for thread in threads:
        thread.join(5)
    assert flags["closed"]
    with profile_lock(accounts.root / "browser-lock", accounts.host_id[9:]):
        pass
    diagnostic = (accounts.root / "login-diagnostics.json").read_text(encoding="utf-8")
    assert all(secret not in diagnostic for secret in ("test-code", "access-test", "refresh-new", "DO-NOT-LOG", exchange["nonce"]))
    record = json.loads(diagnostic)
    if outcome == "exchange_rejected":
        assert record["events"][-2]["stage"] == "exchange_started"
        assert record["events"][-1]["request_id"] == "req_test_rejected"
    else:
        assert record["stage"] == ("account_saved" if outcome == "success" else "failed")
    auth.client.close()
    original.close()


def test_identity_only_does_not_authorize_inference(service):
    auth, accounts, signed, _exchange, requests = service
    claims = auth.verify_identity(signed(), "oaiapp_test")
    item = accounts.connect(claims, {"access_token": "a", "scope": "openid", "expires_at": time.time() + 100}, "oaiapp_test")
    assert not item["ready"]
    with pytest.raises(PlanError, match="Chưa cấp quyền"):
        auth.access_token(item["id"])
    assert not any(r.url.path == "/token" for r in requests)


def test_basic_profile_saved_from_verified_identity_without_inventing_plan(service):
    auth, accounts, signed, _exchange, _requests = service
    claims = auth.verify_identity(signed(name="Cô giáo thử nghiệm"), "oaiapp_test")
    item = accounts.connect(claims, {"scope": PLAN_SCOPE, "access_token": "DO-NOT-SAVE-IN-PROFILE"}, "oaiapp_test")
    accounts.reload()
    saved = accounts.get(item["id"])
    assert saved["name"] == "Cô giáo thử nghiệm" and saved["email"] == "teacher@example.test"
    assert saved["saved_at"] <= time.time() and saved["ready"]
    assert not saved["plan"]  # Permission and identity are not a subscription claim.
    assert "DO-NOT-SAVE-IN-PROFILE" not in accounts.path.read_text(encoding="utf-8")


def test_refresh_rotates_token_and_rechecks_permission(service):
    auth, accounts, signed, exchange, requests = service
    item = accounts.connect(auth.verify_identity(signed(), "oaiapp_test"),
        {"access_token": "old", "refresh_token": "old-refresh", "scope": PLAN_SCOPE, "expires_at": 1}, "oaiapp_test")
    assert auth.access_token(item["id"]) == "access-test"
    assert accounts.secrets.read(item["id"])["refresh_token"] == "refresh-new"
    assert len([r for r in requests if r.url.path == "/token"]) == 1
    assert auth.access_token(item["id"]) == "access-test"
    tokens = accounts.secrets.read(item["id"])
    tokens["expires_at"] = 1
    accounts.secrets.write(item["id"], tokens)
    exchange["scope"] = "openid"
    with pytest.raises(PlanError, match="thu hồi"):
        auth.access_token(item["id"])


def test_selected_account_not_automatically_rotated_and_disconnect(service):
    auth, accounts, signed, _exchange, _requests = service
    first = accounts.connect(auth.verify_identity(signed(sub="one"), "oaiapp_test"), {"scope": PLAN_SCOPE}, "oaiapp_test")
    second = accounts.connect(auth.verify_identity(signed(sub="two"), "oaiapp_test"), {"scope": "openid"}, "oaiapp_test")
    assert accounts.preferred()["id"] == second["id"]
    accounts.select(first["id"])
    assert accounts.preferred()["id"] == first["id"]
    assert not auth.disconnect(first["id"])
    assert accounts.get()["id"] == second["id"]


def test_windows_store_never_writes_plaintext(tmp_path):
    import os
    from uuid import uuid4
    if os.name != "nt":
        pytest.skip("Windows DPAPI")
    secrets = WindowsSecrets(tmp_path)
    account_id = str(uuid4())
    values = {"access_token": "do-not-write-in-plain", "refresh_token": "private-refresh"}
    secrets.write(account_id, values)
    raw = secrets.path(account_id).read_bytes()
    assert all(v.encode() not in raw for v in values.values())
    assert secrets.read(account_id) == values
    secrets.remove(account_id)
    assert not secrets.path(account_id).exists()
