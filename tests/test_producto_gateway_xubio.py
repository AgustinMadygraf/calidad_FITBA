import httpx
import pytest

import src.infrastructure.httpx.producto_gateway_xubio as producto_gateway
from src.infrastructure.httpx.producto_gateway_xubio import (
    ProductoGatewayConfig,
    XubioProductoGateway,
    _extract_producto_id,
    _match_producto_id,
)
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    producto_gateway._GLOBAL_LIST_CACHE.clear()
    producto_gateway._GLOBAL_ITEM_CACHE.clear()
    yield
    producto_gateway._GLOBAL_LIST_CACHE.clear()
    producto_gateway._GLOBAL_ITEM_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"productoid": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
    )
    gw = XubioProductoGateway()
    assert gw.list() == [{"productoid": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"productoid": 2}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
    )
    gw = XubioProductoGateway()
    assert gw.list() == [{"productoid": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
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
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
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
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
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
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
    )
    gw = XubioProductoGateway()
    assert gw.get(10) == {"productoid": 10}


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"productoid": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
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
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
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
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
    )
    gw = XubioProductoGateway()
    assert gw.get(12) == {"productoid": 12}


def test_prod_mode_disables_get_cache(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"productoid": 8}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.producto_gateway_xubio.request_with_token",
        fake_request,
    )
    monkeypatch.setenv("IS_PROD", "true")

    gw = XubioProductoGateway()
    assert gw.list() == [{"productoid": 8}]
    assert gw.list() == [{"productoid": 8}]
    assert calls["count"] == 2


def test_init_disables_fallback_when_primary_equals_fallback():
    gw = XubioProductoGateway(
        config=ProductoGatewayConfig(
            primary_bean="ProductoVentaBean", fallback_bean="ProductoVentaBean"
        )
    )
    assert gw._fallback_bean is None


def test_get_uses_cached_primary_item(monkeypatch):
    gw = XubioProductoGateway(list_cache_ttl=60)
    gw._store_item_cache("ProductoVentaBean", 90, {"productoid": 90})

    monkeypatch.setattr(
        producto_gateway,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No debe llamar HTTP")
        ),
    )

    assert gw.get(90) == {"productoid": 90}


def test_get_uses_cached_fallback_item(monkeypatch):
    gw = XubioProductoGateway(list_cache_ttl=60)
    gw._store_item_cache("ProductoCompraBean", 91, {"productoid": 91})

    monkeypatch.setattr(
        producto_gateway,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No debe llamar HTTP")
        ),
    )

    assert gw.get(91) == {"productoid": 91}


def test_create_update_delete_clear_cache(monkeypatch):
    gw = XubioProductoGateway(list_cache_ttl=60)
    gw._store_cache("ProductoVentaBean", [{"productoid": 1}])
    gw._store_item_cache("ProductoVentaBean", 1, {"productoid": 1})

    monkeypatch.setattr(
        producto_gateway, "create_item", lambda **_kwargs: {"productoid": 2}
    )
    created = gw.create({"nombre": "P2"})
    assert created == {"productoid": 2}
    assert "ProductoVentaBean" not in producto_gateway._GLOBAL_LIST_CACHE

    gw._store_cache("ProductoVentaBean", [{"productoid": 1}])
    gw._store_item_cache("ProductoVentaBean", 1, {"productoid": 1})
    monkeypatch.setattr(
        producto_gateway, "update_item", lambda **_kwargs: {"productoid": 1, "nombre": "U"}
    )
    updated = gw.update(1, {"nombre": "U"})
    assert updated == {"productoid": 1, "nombre": "U"}
    assert "ProductoVentaBean" not in producto_gateway._GLOBAL_LIST_CACHE
    assert (
        producto_gateway._producto_item_cache_key("ProductoVentaBean", 1)
        not in producto_gateway._GLOBAL_ITEM_CACHE
    )

    gw._store_cache("ProductoVentaBean", [{"productoid": 1}])
    gw._store_item_cache("ProductoVentaBean", 1, {"productoid": 1})
    monkeypatch.setattr(producto_gateway, "delete_item", lambda **_kwargs: True)
    assert gw.delete(1) is True
    assert "ProductoVentaBean" not in producto_gateway._GLOBAL_LIST_CACHE
    assert (
        producto_gateway._producto_item_cache_key("ProductoVentaBean", 1)
        not in producto_gateway._GLOBAL_ITEM_CACHE
    )


def test_fetch_list_and_get_wrap_http_error(monkeypatch):
    request = httpx.Request("GET", "https://xubio.local")

    def boom(*_args, **_kwargs):
        raise httpx.ConnectError("boom", request=request)

    monkeypatch.setattr(producto_gateway, "request_with_token", boom)
    gw = XubioProductoGateway()

    with pytest.raises(ExternalServiceError):
        gw._fetch_list_with_fallback("ProductoVentaBean", None)
    with pytest.raises(ExternalServiceError):
        gw._get_from_bean("ProductoVentaBean", 1)


def test_store_item_cache_none_and_clear_item_cache_for_bean():
    gw = XubioProductoGateway(list_cache_ttl=60)
    gw._store_item_cache("ProductoVentaBean", 1, None)
    assert producto_gateway._GLOBAL_ITEM_CACHE == {}

    gw._store_item_cache("ProductoVentaBean", 1, {"productoid": 1})
    gw._store_item_cache("ProductoVentaBean", 2, {"productoid": 2})
    gw._store_item_cache("ProductoCompraBean", 3, {"productoid": 3})
    gw._clear_item_cache("ProductoVentaBean")

    assert (
        producto_gateway._producto_item_cache_key("ProductoVentaBean", 1)
        not in producto_gateway._GLOBAL_ITEM_CACHE
    )
    assert (
        producto_gateway._producto_item_cache_key("ProductoVentaBean", 2)
        not in producto_gateway._GLOBAL_ITEM_CACHE
    )
    assert (
        producto_gateway._producto_item_cache_key("ProductoCompraBean", 3)
        in producto_gateway._GLOBAL_ITEM_CACHE
    )


def test_match_and_extract_producto_id_helpers():
    assert _match_producto_id({"productoid": 7}, 7) is True
    assert _match_producto_id({"productoId": 7}, 7) is True
    assert _match_producto_id({"ID": 7}, 7) is True
    assert _match_producto_id({"id": 7}, 7) is True
    assert _match_producto_id({"id": 6}, 7) is False

    assert _extract_producto_id({"productoid": 8}) == 8
    assert _extract_producto_id({"productoId": 9}) == 9
    assert _extract_producto_id({"ID": 10}) == 10
    assert _extract_producto_id({"id": 11}) == 11
    assert _extract_producto_id({"id": "x"}) is None
