import httpx
import pytest

import src.infrastructure.httpx.cliente_gateway_xubio as cliente_gateway
from src.infrastructure.httpx.cliente_gateway_xubio import XubioClienteGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    cliente_gateway._GLOBAL_LIST_CACHE.clear()
    cliente_gateway._GLOBAL_ITEM_CACHE.clear()
    yield
    cliente_gateway._GLOBAL_LIST_CACHE.clear()
    cliente_gateway._GLOBAL_ITEM_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"cliente_id": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway()
    assert gw.list() == [{"cliente_id": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"cliente_id": 2}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway()
    assert gw.list() == [{"cliente_id": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"cliente_id": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway(list_cache_ttl=60)
    assert gw.list() == [{"cliente_id": 1}]
    assert gw.list() == [{"cliente_id": 1}]
    assert calls["count"] == 1


def test_create_invalidates_list_cache(monkeypatch):
    calls = {"list": 0, "create": 0}

    def fake_request(method, url, **_kwargs):
        if method == "GET" and url.endswith("/clienteBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"cliente_id": 1}])
        if method == "POST" and url.endswith("/clienteBean"):
            calls["create"] += 1
            return httpx.Response(200, json={"cliente_id": 2})
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway(list_cache_ttl=60)
    assert gw.list() == [{"cliente_id": 1}]
    assert gw.list() == [{"cliente_id": 1}]
    assert calls["list"] == 1
    assert gw.create({"razonSocial": "Nuevo"}) == {"cliente_id": 2}
    assert calls["create"] == 1
    assert gw.list() == [{"cliente_id": 1}]
    assert calls["list"] == 2


def test_prod_mode_disables_get_cache(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"clienteId": 3}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    monkeypatch.setenv("IS_PROD", "true")

    gw = XubioClienteGateway()
    assert gw.list() == [{"clienteId": 3}]
    assert gw.list() == [{"clienteId": 3}]
    assert calls["count"] == 2


def test_single_flow_covers_get_update_delete_and_ttl_zero(monkeypatch):
    calls = {"list": 0, "get": 0, "update": 0, "delete": 0}

    def fake_request(method, url, **_kwargs):
        if method == "GET" and url.endswith("/clienteBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"clienteId": 7}])
        if method == "GET" and url.endswith("/clienteBean/7"):
            calls["get"] += 1
            return httpx.Response(200, json={"cliente_id": 7})
        if method == "PUT" and url.endswith("/clienteBean/7"):
            calls["update"] += 1
            return httpx.Response(200, json={"cliente_id": 7, "updated": True})
        if method == "DELETE" and url.endswith("/clienteBean/7"):
            calls["delete"] += 1
            return httpx.Response(200, json={"status": "ok"})
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )

    gw = XubioClienteGateway(list_cache_ttl=60)
    assert gw.list() == [{"clienteId": 7}]
    assert gw.get(7) == {"clienteId": 7}
    assert calls["get"] == 0

    assert gw.update(7, {"razonSocial": "Editado"}) == {
        "cliente_id": 7,
        "updated": True,
    }
    assert calls["update"] == 1
    assert gw.get(7) == {"cliente_id": 7}
    assert calls["get"] == 1

    assert gw.delete(7) is True
    assert calls["delete"] == 1
    assert gw.list() == [{"clienteId": 7}]
    assert calls["list"] == 2

    gw_no_cache = XubioClienteGateway(list_cache_ttl=0)
    assert gw_no_cache.list() == [{"clienteId": 7}]
    assert gw_no_cache.list() == [{"clienteId": 7}]
    assert calls["list"] == 4
