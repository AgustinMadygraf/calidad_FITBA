import httpx
import pytest

import src.infrastructure.httpx.moneda_gateway_xubio as moneda_gateway
from src.infrastructure.httpx.moneda_gateway_xubio import XubioMonedaGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    moneda_gateway._GLOBAL_LIST_CACHE.clear()
    yield
    moneda_gateway._GLOBAL_LIST_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"codigo": "ARS", "id": 0, "ID": 0}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioMonedaGateway()
    assert gw.list() == [{"codigo": "ARS", "id": 0, "ID": 0}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(
            200, json={"items": [{"codigo": "USD", "id": 1, "ID": 1}]}
        )

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioMonedaGateway()
    assert gw.list() == [{"codigo": "USD", "id": 1, "ID": 1}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioMonedaGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_get_reads_from_list_only(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/monedaBean/0"):
            raise AssertionError("No debe llamar al endpoint detalle de moneda")
        if url.endswith("/monedaBean"):
            return httpx.Response(200, json=[{"codigo": "ARS", "id": 0, "ID": 0}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioMonedaGateway()
    assert gw.get(0) == {"codigo": "ARS", "id": 0, "ID": 0}


def test_get_returns_none_when_missing(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/monedaBean/999"):
            raise AssertionError("No debe llamar al endpoint detalle de moneda")
        if url.endswith("/monedaBean"):
            return httpx.Response(200, json=[{"codigo": "ARS", "id": 0, "ID": 0}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioMonedaGateway()
    assert gw.get(999) is None


def test_get_uses_single_list_lookup_when_missing(monkeypatch):
    calls = {"list": 0}

    def fake_request(_method, url, **_kwargs):
        if url.endswith("/monedaBean/999"):
            raise AssertionError("No debe llamar al endpoint detalle de moneda")
        if url.endswith("/monedaBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"codigo": "ARS", "id": 0, "ID": 0}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioMonedaGateway()
    assert gw.get(999) is None
    assert calls["list"] == 1


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"codigo": "ARS", "id": 0, "ID": 0}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioMonedaGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "ARS", "id": 0, "ID": 0}]
    assert gw.list() == [{"codigo": "ARS", "id": 0, "ID": 0}]
    assert calls["count"] == 1
