import httpx
import pytest

import src.infrastructure.httpx.vendedor_gateway_xubio as vendedor_gateway
from src.infrastructure.httpx.vendedor_gateway_xubio import XubioVendedorGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    vendedor_gateway._GLOBAL_LIST_CACHE.clear()
    yield
    vendedor_gateway._GLOBAL_LIST_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"vendedorId": 1, "nombre": "Ana"}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioVendedorGateway()
    assert gw.list() == [{"vendedorId": 1, "nombre": "Ana"}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"vendedorId": 2, "nombre": "Luis"}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioVendedorGateway()
    assert gw.list() == [{"vendedorId": 2, "nombre": "Luis"}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioVendedorGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_get_reads_from_list_only(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/vendedorBean/1"):
            raise AssertionError("No debe llamar al endpoint detalle de vendedor")
        if url.endswith("/vendedorBean"):
            return httpx.Response(200, json=[{"vendedorId": 1, "nombre": "Ana"}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioVendedorGateway()
    assert gw.get(1) == {"vendedorId": 1, "nombre": "Ana"}


def test_get_returns_none_when_missing(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/vendedorBean/999"):
            raise AssertionError("No debe llamar al endpoint detalle de vendedor")
        if url.endswith("/vendedorBean"):
            return httpx.Response(200, json=[{"vendedorId": 1, "nombre": "Ana"}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioVendedorGateway()
    assert gw.get(999) is None


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"vendedorId": 1, "nombre": "Ana"}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioVendedorGateway(list_cache_ttl=60)
    assert gw.list() == [{"vendedorId": 1, "nombre": "Ana"}]
    assert gw.list() == [{"vendedorId": 1, "nombre": "Ana"}]
    assert calls["count"] == 1
