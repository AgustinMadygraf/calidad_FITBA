import base64
import json
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app
from src.infrastructure.fastapi.routers import auth as auth_router


def test_auth_session_returns_unauthenticated_payload_when_missing_cookie():
    client = TestClient(app)
    response = client.get("/auth/session", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "user": None}


def test_auth_login_google_returns_url_payload():
    client = TestClient(app)
    response = client.post(
        "/auth/login/google",
        json={"redirectPath": "/remitos"},
        headers={"Origin": "http://127.0.0.1:5173"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data["url"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")


def test_auth_login_google_rejects_invalid_redirect_path():
    client = TestClient(app)
    response = client.post(
        "/auth/login/google",
        json={"redirectPath": "https://evil.com"},
        headers={"Origin": "http://127.0.0.1:5173"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "redirectPath invalido"


def test_auth_logout_is_idempotent_and_expires_cookie():
    client = TestClient(app)
    response = client.post(
        "/auth/logout", json={}, headers={"Origin": "http://127.0.0.1:5173"}
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    cookie_header = response.headers.get("set-cookie", "")
    assert "xubio_session=" in cookie_header


def test_auth_session_returns_authenticated_payload_when_valid_session_cookie():
    client = TestClient(app)
    auth_router._SESSIONS.clear()
    auth_router._SESSIONS["sid-test"] = auth_router._SessionData(
        user={
            "id": "usr_123",
            "email": "usuario@dominio.com",
            "name": "Nombre Apellido",
            "pictureUrl": "https://example.com/pic.jpg",
        },
        expires_at=32503680000.0,
    )
    client.cookies.set("xubio_session", "sid-test")

    response = client.get("/auth/session")
    assert response.status_code == 200
    assert response.json()["authenticated"] is True
    assert response.json()["user"]["id"] == "usr_123"


def _build_unsigned_jwt(payload):
    header = {"alg": "none", "typ": "JWT"}
    enc = lambda obj: base64.urlsafe_b64encode(  # noqa: E731
        json.dumps(obj, separators=(",", ":")).encode("utf-8")
    ).decode("ascii").rstrip("=")
    return f"{enc(header)}.{enc(payload)}."


def test_auth_callback_google_creates_session_and_redirects(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google-client-secret")
    client = TestClient(app)

    start = client.post(
        "/auth/login/google",
        json={"redirectPath": "/remitos"},
        headers={"Origin": "http://127.0.0.1:5173"},
    )
    assert start.status_code == 200
    auth_url = start.json()["url"]
    state = parse_qs(urlparse(auth_url).query)["state"][0]
    tx = auth_router._OIDC_TX[state]

    id_token = _build_unsigned_jwt(
        {
            "iss": "https://accounts.google.com",
            "aud": "google-client-id",
            "exp": 32503680000,
            "nonce": tx.nonce,
            "sub": "usr_abc",
            "email": "test@example.com",
            "name": "Usuario Test",
            "picture": "https://example.com/u.png",
        }
    )

    class _FakeResp:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload

        def json(self):
            return self._payload

    def fake_post(url, data=None, timeout=10.0):
        return _FakeResp(200, {"id_token": id_token})

    def fake_get(url, params=None, timeout=10.0):
        return _FakeResp(200, {"aud": "google-client-id"})

    monkeypatch.setattr(auth_router.httpx, "post", fake_post)
    monkeypatch.setattr(auth_router.httpx, "get", fake_get)

    callback = client.get(
        f"/auth/callback/google?code=authcode123&state={state}", follow_redirects=False
    )
    assert callback.status_code == 302
    assert callback.headers["location"] == "/remitos"
    cookie_header = callback.headers.get("set-cookie", "")
    assert "xubio_session=" in cookie_header

    me = client.get("/auth/session")
    assert me.status_code == 200
    assert me.json()["authenticated"] is True
    assert me.json()["user"]["id"] == "usr_abc"


def test_auth_callback_google_rejects_invalid_state():
    client = TestClient(app)
    response = client.get("/auth/callback/google?code=abc&state=missing")
    assert response.status_code == 400
    assert response.json()["detail"] == "state invalido o expirado"


def test_auth_csrf_rejects_missing_origin_on_post():
    client = TestClient(app)
    response = client.post("/auth/login/google", json={"redirectPath": "/remitos"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Origen requerido"
