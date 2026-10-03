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


@pytest.mark.parametrize("error", ["invalid_client", "access_denied", "subscription_sharing_user_not_eligible"])
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


@pytest.mark.parametrize("reason", ["closed", "cancelled"])
def test_owned_login_browser_cleanup_when_closed_or_cancelled(service, monkeypatch, reason):
    from app import chatgpt_auth

    auth, accounts, _signed, _exchange, _requests = service
    cancel = threading.Event()
    events = []

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
            return False

    monkeypatch.setattr(chatgpt_auth, "PrivateLoginBrowser", Browser)
    with pytest.raises(PlanError) as caught:
        auth.authorize(cancel=cancel, timeout=5)
    assert caught.value.code == ("browser_closed" if reason == "closed" else "cancelled")
    assert events == ["opened", "closed"] and not accounts.data["accounts"]


def test_identity_only_does_not_authorize_inference(service):
    auth, accounts, signed, _exchange, requests = service
    claims = auth.verify_identity(signed(), "oaiapp_test")
    item = accounts.connect(claims, {"access_token": "a", "scope": "openid", "expires_at": time.time() + 100}, "oaiapp_test")
    assert not item["ready"]
    with pytest.raises(PlanError, match="Chưa cấp quyền"):
        auth.access_token(item["id"])
    assert not any(r.url.path == "/token" for r in requests)


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
