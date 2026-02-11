import httpx
import pytest

from src.infrastructure.httpx.identificacion_tributaria_gateway_xubio import (
    XubioIdentificacionTributariaGateway,
)
from src.use_cases.errors import ExternalServiceError


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


def test_get_falls_back_to_list_on_404(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/identificacionTributaria/9"):
            return httpx.Response(404)
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
            return httpx.Response(404)
        if url.endswith("/identificacionTributaria"):
            return httpx.Response(200, json=[{"codigo": "CUIT", "id": 9, "ID": 9}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioIdentificacionTributariaGateway()
    assert gw.get(999) is None
