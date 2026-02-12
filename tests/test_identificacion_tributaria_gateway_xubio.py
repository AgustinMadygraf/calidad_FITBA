import httpx
import pytest

from src.infrastructure.httpx import (
    identificacion_tributaria_gateway_xubio as idtrib_gateway,
)
from src.infrastructure.httpx.identificacion_tributaria_gateway_xubio import (
    XubioIdentificacionTributariaGateway,
)
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    idtrib_gateway._GLOBAL_LIST_CACHE.clear()
    yield
    idtrib_gateway._GLOBAL_LIST_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"codigo": "CUIT", "id": 9, "ID": 9}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioIdentificacionTributariaGateway()
    assert gw.list() == [{"codigo": "CUIT", "id": 9, "ID": 9}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(
            200, json={"items": [{"codigo": "DNI", "id": 10, "ID": 10}]}
        )

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioIdentificacionTributariaGateway()
    assert gw.list() == [{"codigo": "DNI", "id": 10, "ID": 10}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioIdentificacionTributariaGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_get_reads_from_list_only(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/identificacionTributaria/9"):
            raise AssertionError(
                "No debe llamar al endpoint detalle de identificacionTributaria"
            )
        if url.endswith("/identificacionTributaria"):
            return httpx.Response(200, json=[{"codigo": "CUIT", "id": 9, "ID": 9}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioIdentificacionTributariaGateway()
    assert gw.get(9) == {"codigo": "CUIT", "id": 9, "ID": 9}


def test_get_returns_none_when_missing(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/identificacionTributaria/999"):
            raise AssertionError(
                "No debe llamar al endpoint detalle de identificacionTributaria"
            )
        if url.endswith("/identificacionTributaria"):
            return httpx.Response(200, json=[{"codigo": "CUIT", "id": 9, "ID": 9}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioIdentificacionTributariaGateway()
    assert gw.get(999) is None


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"codigo": "CUIT", "id": 9, "ID": 9}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioIdentificacionTributariaGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "CUIT", "id": 9, "ID": 9}]
    assert gw.list() == [{"codigo": "CUIT", "id": 9, "ID": 9}]
    assert calls["count"] == 1
