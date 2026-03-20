import httpx
import pytest

import src.infrastructure.httpx.categoria_fiscal_gateway_xubio as categoria_gateway
from src.infrastructure.httpx.categoria_fiscal_gateway_xubio import (
    XubioCategoriaFiscalGateway,
)
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    categoria_gateway._GLOBAL_LIST_CACHE.clear()
    yield
    categoria_gateway._GLOBAL_LIST_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"codigo": "RI", "id": 1, "ID": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCategoriaFiscalGateway()
    assert gw.list() == [{"codigo": "RI", "id": 1, "ID": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(
            200, json={"items": [{"codigo": "CF", "id": 3, "ID": 3}]}
        )

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCategoriaFiscalGateway()
    assert gw.list() == [{"codigo": "CF", "id": 3, "ID": 3}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCategoriaFiscalGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_get_reads_from_list_only(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/categoriaFiscal/1"):
            raise AssertionError(
                "No debe llamar al endpoint detalle de categoriaFiscal"
            )
        if url.endswith("/categoriaFiscal"):
            return httpx.Response(200, json=[{"codigo": "RI", "id": 1, "ID": 1}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCategoriaFiscalGateway()
    assert gw.get(1) == {"codigo": "RI", "id": 1, "ID": 1}


def test_get_returns_none_when_missing(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/categoriaFiscal/999"):
            raise AssertionError(
                "No debe llamar al endpoint detalle de categoriaFiscal"
            )
        if url.endswith("/categoriaFiscal"):
            return httpx.Response(200, json=[{"codigo": "RI", "id": 1, "ID": 1}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCategoriaFiscalGateway()
    assert gw.get(999) is None


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"codigo": "RI", "id": 1, "ID": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCategoriaFiscalGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "RI", "id": 1, "ID": 1}]
    assert gw.list() == [{"codigo": "RI", "id": 1, "ID": 1}]
    assert calls["count"] == 1
