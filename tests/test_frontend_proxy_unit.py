import asyncio

import pytest
from fastapi import WebSocketDisconnect
from fastapi import Response as FastAPIResponse
from starlette.requests import Request

from src.infrastructure.fastapi import frontend_proxy
from src.infrastructure.fastapi import frontend_proxy_ws as proxy_ws
from src.infrastructure.fastapi.frontend_proxy_ws import (
    _to_ws_url,
    build_frontend_ws_proxy_handler,
)


def test_is_frontend_route_exclusions():
    assert frontend_proxy.is_frontend_route("/remitos") is True
    assert frontend_proxy.is_frontend_route("/assets/main.js") is True
    assert frontend_proxy.is_frontend_route("/API/1.1/clienteBean") is False
    assert frontend_proxy.is_frontend_route("/health") is False
    assert frontend_proxy.is_frontend_route("/token/inspect") is False
    assert frontend_proxy.is_frontend_route("/docs") is False
    assert frontend_proxy.is_frontend_route("/debug/clienteBean") is False
    assert frontend_proxy.is_frontend_route("/observability/events") is False
    assert frontend_proxy.is_frontend_route("/favicon.ico") is False


@pytest.mark.parametrize(
    "base_url,path,query,expected",
    [
        (
            "http://127.0.0.1:5173",
            "remitos",
            "",
            "ws://127.0.0.1:5173/remitos",
        ),
        (
            "https://frontend.example.dev/base",
            "@vite/client",
            "t=1",
            "wss://frontend.example.dev/base/@vite/client?t=1",
        ),
    ],
)
def test_to_ws_url(base_url, path, query, expected):
    assert _to_ws_url(base_url, path, query) == expected


def test_ws_proxy_returns_1011_when_dependency_missing(monkeypatch):
    monkeypatch.setattr(proxy_ws, "websockets", None)
    handler = build_frontend_ws_proxy_handler("http://127.0.0.1:5173")

    class FakeWebSocket:
        def __init__(self):
            self.closed = None
            self.scope = {"query_string": b"", "subprotocols": []}
            self.headers = []

        async def close(self, code, reason=None):
            self.closed = (code, reason)

    ws = FakeWebSocket()
    asyncio.run(handler(ws, "@vite/client"))

    assert ws.closed == (1011, "WS proxy dependency missing")


def test_ws_proxy_rejects_non_frontend_route(monkeypatch):
    monkeypatch.setattr(proxy_ws, "websockets", object())

    class FakeWebSocket:
        def __init__(self):
            self.closed = None
            self.scope = {"query_string": b"", "subprotocols": []}
            self.headers = {}

        async def close(self, code, reason=None):
            self.closed = (code, reason)

    ws = FakeWebSocket()
    handler = build_frontend_ws_proxy_handler("http://127.0.0.1:5173")
    asyncio.run(handler(ws, "API/1.1/clienteBean"))
    assert ws.closed == (1008, "Not a frontend websocket route")


def test_ws_proxy_bidirectional_and_disconnect(monkeypatch):
    events = {"connect_calls": []}

    class FakeUpstream:
        subprotocol = "vite-hmr"

        def __init__(self):
            self.sent = []
            self.closed = None
            self._incoming = iter(["hmr-msg", b"\x01"])

        async def send(self, payload):
            self.sent.append(payload)

        async def close(self, code=1000):
            self.closed = code

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self._incoming)
            except StopIteration:
                raise StopAsyncIteration

    class FakeUpstreamContext:
        def __init__(self, upstream):
            self._upstream = upstream

        async def __aenter__(self):
            return self._upstream

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeWebsocketsModule:
        @staticmethod
        def connect(url, **kwargs):
            events["connect_calls"].append((url, kwargs))
            return FakeUpstreamContext(upstream)

    class FakeWebSocket:
        def __init__(self):
            self.accepted = None
            self.closed = None
            self.sent_text = []
            self.sent_bytes = []
            self.scope = {"query_string": b"t=42", "subprotocols": ["vite-hmr"]}
            self.headers = {
                "host": "localhost:8000",
                "x-test": "ok",
                "sec-websocket-key": "masked",
            }
            self._received = iter(
                [
                    {"type": "websocket.receive", "text": "ping"},
                    {"type": "websocket.receive", "bytes": b"\x02"},
                    {"type": "websocket.disconnect"},
                ]
            )

        async def accept(self, subprotocol=None):
            self.accepted = subprotocol

        async def receive(self):
            return next(self._received)

        async def send_text(self, payload):
            self.sent_text.append(payload)

        async def send_bytes(self, payload):
            self.sent_bytes.append(payload)

        async def close(self, code, reason=None):
            self.closed = (code, reason)

    upstream = FakeUpstream()
    ws = FakeWebSocket()
    monkeypatch.setattr(proxy_ws, "websockets", FakeWebsocketsModule())
    handler = build_frontend_ws_proxy_handler("http://127.0.0.1:5173")
    asyncio.run(handler(ws, "@vite/client"))

    assert ws.accepted == "vite-hmr"
    assert ws.sent_text == ["hmr-msg"]
    assert ws.sent_bytes == [b"\x01"]
    assert upstream.sent == ["ping", b"\x02"]
    assert upstream.closed == 1000
    assert ws.closed == (1000, None)
    url, kwargs = events["connect_calls"][0]
    assert url == "ws://127.0.0.1:5173/@vite/client?t=42"
    assert kwargs["subprotocols"] == ["vite-hmr"]
    assert kwargs["additional_headers"] == {"x-test": "ok"}


def test_ws_proxy_falls_back_to_extra_headers_on_type_error(monkeypatch):
    calls = []

    class FakeUpstream:
        subprotocol = None

        async def close(self, code=1000):
            return None

        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    class FakeUpstreamContext:
        async def __aenter__(self):
            return FakeUpstream()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeWebsocketsModule:
        @staticmethod
        def connect(url, **kwargs):
            calls.append(kwargs.copy())
            if "additional_headers" in kwargs:
                raise TypeError("unexpected kwarg")
            return FakeUpstreamContext()

    class FakeWebSocket:
        def __init__(self):
            self.scope = {"query_string": b"", "subprotocols": []}
            self.headers = {"x-test": "ok"}

        async def accept(self, subprotocol=None):
            return None

        async def receive(self):
            raise WebSocketDisconnect()

        async def close(self, code, reason=None):
            return None

    monkeypatch.setattr(proxy_ws, "websockets", FakeWebsocketsModule())
    handler = build_frontend_ws_proxy_handler("http://127.0.0.1:5173")
    asyncio.run(handler(FakeWebSocket(), "remitos"))
    assert "additional_headers" in calls[0]
    assert "extra_headers" in calls[1]


def test_ws_proxy_returns_1013_on_upstream_oserror(monkeypatch):
    class FakeWebsocketsModule:
        @staticmethod
        def connect(url, **kwargs):
            raise OSError("down")

    class FakeWebSocket:
        def __init__(self):
            self.closed = None
            self.scope = {"query_string": b"", "subprotocols": []}
            self.headers = {}

        async def close(self, code, reason=None):
            self.closed = (code, reason)

    ws = FakeWebSocket()
    monkeypatch.setattr(proxy_ws, "websockets", FakeWebsocketsModule())
    handler = build_frontend_ws_proxy_handler("http://127.0.0.1:5173")
    asyncio.run(handler(ws, "remitos"))
    assert ws.closed == (1013, "Frontend dev server unavailable")


def _build_request(method: str, path: str, query_string: str = "", headers=None):
    raw_headers = [
        (key.lower().encode("latin-1"), value.encode("latin-1"))
        for key, value in (headers or {}).items()
    ]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "query_string": query_string.encode("ascii"),
        "headers": raw_headers,
        "client": ("127.0.0.1", 12345),
        "server": ("localhost", 8000),
    }

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


def test_http_proxy_skips_non_frontend_or_non_get_head():
    middleware = frontend_proxy.build_frontend_proxy_middleware("http://127.0.0.1:5173")
    fallback_calls = {"n": 0}

    async def call_next(_request):
        fallback_calls["n"] += 1
        return FastAPIResponse(content=b"fallback", status_code=200)

    request_post = _build_request("POST", "/remitos")
    response_post = asyncio.run(middleware(request_post, call_next))
    assert response_post.status_code == 200

    request_api = _build_request("GET", "/API/1.1/clienteBean")
    response_api = asyncio.run(middleware(request_api, call_next))
    assert response_api.status_code == 200
    assert fallback_calls["n"] == 2


def test_http_proxy_success(monkeypatch):
    middleware = frontend_proxy.build_frontend_proxy_middleware("http://127.0.0.1:5173")
    sent = {}

    class FakeUpstreamResponse:
        status_code = 200
        content = b"<html>vite</html>"
        headers = {
            "content-type": "text/html; charset=utf-8",
            "cache-control": "no-cache",
            "connection": "keep-alive",
        }

    class FakeAsyncClient:
        def __init__(self, timeout):
            assert timeout == 1.5

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def build_request(self, method, target_url, headers=None):
            sent["built"] = (method, target_url, headers)
            return object()

        async def send(self, _proxied):
            return FakeUpstreamResponse()

    monkeypatch.setattr(frontend_proxy.httpx, "AsyncClient", FakeAsyncClient)

    async def call_next(_request):
        return FastAPIResponse(content=b"fallback", status_code=599)

    request = _build_request(
        "GET",
        "/@vite/client",
        "t=123",
        {"Host": "localhost:8000", "X-Test": "ok", "Connection": "close"},
    )
    response = asyncio.run(middleware(request, call_next))
    assert response.status_code == 200
    assert response.body == b"<html>vite</html>"
    assert response.headers["cache-control"] == "no-cache"
    assert "connection" not in {k.lower() for k in response.headers.keys()}
    method, target_url, headers = sent["built"]
    assert method == "GET"
    assert target_url == "http://127.0.0.1:5173/@vite/client?t=123"
    assert headers == {"x-test": "ok"}


@pytest.mark.parametrize(
    "error_factory",
    [
        lambda: frontend_proxy.httpx.ConnectError("down"),
        lambda: frontend_proxy.httpx.ConnectTimeout("timeout"),
        lambda: frontend_proxy.httpx.ReadTimeout("read-timeout"),
        lambda: frontend_proxy.httpx.HTTPError("generic-http-error"),
    ],
)
def test_http_proxy_fallback_on_upstream_errors(monkeypatch, error_factory):
    middleware = frontend_proxy.build_frontend_proxy_middleware("http://127.0.0.1:5173")
    fallback_calls = {"n": 0}

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def build_request(self, method, target_url, headers=None):
            return object()

        async def send(self, _proxied):
            raise error_factory()

    monkeypatch.setattr(frontend_proxy.httpx, "AsyncClient", FakeAsyncClient)

    async def call_next(_request):
        fallback_calls["n"] += 1
        return FastAPIResponse(content=b"fallback", status_code=207)

    request = _build_request("GET", "/remitos")
    response = asyncio.run(middleware(request, call_next))
    assert response.status_code == 207
    assert fallback_calls["n"] == 1
