import httpx
import pytest

import src.infrastructure.httpx.producto_gateway_xubio as producto_gateway
from src.infrastructure.httpx.producto_gateway_xubio import XubioProductoGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    producto_gateway._GLOBAL_LIST_CACHE.clear()
    yield
    producto_gateway._GLOBAL_LIST_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"productoid": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    assert gw.list() == [{"productoid": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"productoid": 2}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    assert gw.list() == [{"productoid": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_list_falls_back_to_compra_on_5xx(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if "ProductoVentaBean" in url:
            return httpx.Response(500, text="boom")
        if "ProductoCompraBean" in url:
            return httpx.Response(200, json=[{"productoid": 3}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    assert gw.list() == [{"productoid": 3}]


def test_get_falls_back_to_list_on_5xx(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if "ProductoVentaBean/9" in url:
            return httpx.Response(500, text="boom")
        if url.endswith("ProductoVentaBean"):
            return httpx.Response(200, json=[{"productoid": 9}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    assert gw.get(9) == {"productoid": 9}


def test_get_falls_back_to_list_on_404(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if "ProductoVentaBean/10" in url:
            return httpx.Response(404)
        if url.endswith("ProductoVentaBean"):
            return httpx.Response(200, json=[{"productoid": 10}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    assert gw.get(10) == {"productoid": 10}


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"productoid": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway(list_cache_ttl=60)
    other = XubioProductoGateway(list_cache_ttl=60)
    assert gw.list() == [{"productoid": 1}]
    assert other.list() == [{"productoid": 1}]
    assert calls["count"] == 1


def test_get_falls_back_to_compra_when_not_in_list(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if "ProductoVentaBean/11" in url:
            return httpx.Response(404)
        if url.endswith("ProductoVentaBean"):
            return httpx.Response(200, json=[{"productoid": 1}])
        if "ProductoCompraBean/11" in url:
            return httpx.Response(200, json={"productoid": 11})
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    assert gw.get(11) == {"productoid": 11}


def test_get_falls_back_to_compra_list_on_5xx(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if "ProductoVentaBean/12" in url:
            return httpx.Response(500, text="boom")
        if url.endswith("ProductoVentaBean"):
            return httpx.Response(200, json=[{"productoid": 1}])
        if "ProductoCompraBean/12" in url:
            return httpx.Response(500, text="boom")
        if "ProductoCompraBean" in url:
            return httpx.Response(200, json=[{"productoid": 12}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioProductoGateway()
    assert gw.get(12) == {"productoid": 12}
