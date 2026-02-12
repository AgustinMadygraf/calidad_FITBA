import base64

import httpx
import pytest

import src.infrastructure.httpx.token_client as token_client


@pytest.fixture(autouse=True)
def reset_token_cache():
    token_client._CACHE.update(
        {
            "access_token": None,
            "token_type": None,
            "scope": None,
            "expires_at": 0,
        }
    )
    yield
    token_client._CACHE.update(
        {
            "access_token": None,
            "token_type": None,
            "scope": None,
            "expires_at": 0,
        }
    )


def test_build_helpers(monkeypatch):
    monkeypatch.setenv("XUBIO_CLIENT_ID", "cid")
    monkeypatch.setenv("XUBIO_SECRET_ID", "sid")
    monkeypatch.setattr(
        token_client, "get_xubio_token_endpoint", lambda: "https://token.local"
    )

    assert token_client.build_token_request() == {"grant_type": "client_credentials"}
    assert token_client.get_token_endpoint() == "https://token.local"

    encoded = token_client.build_auth_header().removeprefix("Basic ")
    assert base64.b64decode(encoded).decode("utf-8") == "cid:sid"


def test_cache_helpers(monkeypatch):
    monkeypatch.setattr(token_client, "_now", lambda: 100)
    token_client._CACHE.update(
        {
            "access_token": "abc",
            "token_type": "Bearer",
            "scope": "all",
            "expires_at": 160,
        }
    )

    assert token_client._cache_valid() is True
    info = token_client._cached_token_info()
    assert info is not None
    assert info["from_cache"] is True
    assert info["expires_in"] == 60

    token_client._CACHE["expires_at"] = 105
    assert token_client._cache_valid() is False
    assert token_client._cached_token_info() is None


def test_preview_token_short_and_long():
    assert token_client._preview_token("short") == "short"
    assert token_client._preview_token("ABCDEFGHIJKL") == "ABCDEF...IJKL"


def test_parse_token_payload_validation():
    with pytest.raises(RuntimeError, match="sin JSON valido"):
        token_client._parse_token_payload(["not", "dict"])

    with pytest.raises(RuntimeError, match="sin access_token"):
        token_client._parse_token_payload({"expires_in": 10})

    with pytest.raises(RuntimeError, match="sin expires_in valido"):
        token_client._parse_token_payload({"access_token": "abc", "expires_in": "x"})

    parsed = token_client._parse_token_payload(
        {
            "access_token": "abc",
            "expires_in": "30",
            "token_type": "Bearer",
            "scope": "read",
        }
    )
    assert parsed == ("abc", 30, "Bearer", "read")


def test_store_token_sets_cache_and_returns_expiry(monkeypatch):
    monkeypatch.setattr(token_client, "_now", lambda: 1000)
    expires_at = token_client._store_token("tok", "Bearer", "r", 50)
    assert expires_at == 1050
    assert token_client._CACHE["access_token"] == "tok"
    assert token_client._CACHE["token_type"] == "Bearer"
    assert token_client._CACHE["scope"] == "r"


def test_request_token_success(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, url, data, headers):
            captured["url"] = url
            captured["data"] = data
            captured["headers"] = headers
            return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(token_client.httpx, "Client", FakeClient)
    monkeypatch.setattr(token_client, "get_token_endpoint", lambda: "https://token")
    monkeypatch.setattr(token_client, "build_auth_header", lambda: "Basic abc")
    monkeypatch.setattr(
        token_client, "build_token_request", lambda: {"grant_type": "client_credentials"}
    )

    response = token_client._request_token(timeout=3.0)

    assert response.status_code == 200
    assert captured["timeout"] == 3.0
    assert captured["url"] == "https://token"
    assert captured["data"] == {"grant_type": "client_credentials"}
    assert captured["headers"]["Authorization"] == "Basic abc"


def test_request_token_raises_on_error(monkeypatch):
    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, _url, **_kwargs):
            return httpx.Response(401, text="bad creds")

    monkeypatch.setattr(token_client.httpx, "Client", FakeClient)
    monkeypatch.setattr(token_client, "get_token_endpoint", lambda: "https://token")
    monkeypatch.setattr(token_client, "build_auth_header", lambda: "Basic abc")

    with pytest.raises(RuntimeError, match="TokenEndpoint error 401"):
        token_client._request_token(timeout=1.0)


def test_fetch_access_token_uses_cache(monkeypatch):
    monkeypatch.setattr(token_client, "_now", lambda: 100)
    token_client._CACHE.update(
        {
            "access_token": "cached",
            "token_type": "Bearer",
            "scope": "read",
            "expires_at": 150,
        }
    )

    def fail_request(_timeout):
        raise AssertionError("No debe pedir token si cache es valido")

    monkeypatch.setattr(token_client, "_request_token", fail_request)
    info = token_client.fetch_access_token(force_refresh=False)

    assert info["from_cache"] is True
    assert info["access_token"] == "cached"


def test_fetch_access_token_force_refresh(monkeypatch):
    monkeypatch.setattr(token_client, "_now", lambda: 10)
    monkeypatch.setattr(
        token_client,
        "_request_token",
        lambda timeout: httpx.Response(
            200,
            json={
                "access_token": "fresh",
                "expires_in": "40",
                "token_type": "Bearer",
                "scope": "all",
            },
        ),
    )

    info = token_client.fetch_access_token(timeout=2.0, force_refresh=True)

    assert info["from_cache"] is False
    assert info["access_token"] == "fresh"
    assert info["expires_in"] == 40
    assert info["expires_at"] == 50


def test_is_invalid_token_response_handles_non_json():
    resp = httpx.Response(200, text="plain")
    assert token_client.is_invalid_token_response(resp) is False


def test_get_token_status_uses_preview_and_remaining(monkeypatch):
    monkeypatch.setattr(token_client, "_now", lambda: 100)
    monkeypatch.setattr(
        token_client,
        "fetch_access_token",
        lambda timeout, force_refresh: {
            "access_token": "1234567890ABCDEF",
            "expires_at": 160,
            "from_cache": True,
        },
    )

    status = token_client.get_token_status(timeout=5.0)

    assert status["token_preview"] == "123456...CDEF"
    assert status["expires_in_seconds"] == 60
    assert status["from_cache"] is True


def test_request_with_token_retries_on_invalid_token(monkeypatch):
    token_calls = []
    request_calls = []

    def fake_fetch(timeout, force_refresh):
        token_calls.append(force_refresh)
        token = "first" if not force_refresh else "second"
        return {"access_token": token}

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def request(self, method, url, **kwargs):
            request_calls.append((method, url, kwargs))
            if len(request_calls) == 1:
                return httpx.Response(401, json={"error": "invalid_token"})
            return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(token_client, "fetch_access_token", fake_fetch)
    monkeypatch.setattr(token_client.httpx, "Client", FakeClient)

    response = token_client.request_with_token(
        "GET",
        "https://xubio.local/recurso",
        timeout=7.0,
        headers={"X-Trace": "1"},
        params={"page": 1},
    )

    assert response.status_code == 200
    assert token_calls == [False, True]
    assert len(request_calls) == 2
    first_headers = request_calls[0][2]["headers"]
    second_headers = request_calls[1][2]["headers"]
    assert first_headers["Authorization"] == "Bearer first"
    assert second_headers["Authorization"] == "Bearer second"
    assert first_headers["X-Trace"] == "1"


def test_request_with_token_rejects_unknown_options():
    with pytest.raises(ValueError, match="Opciones no soportadas"):
        token_client.request_with_token("GET", "https://x", custom_opt=True)
