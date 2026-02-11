import httpx
import pytest

from src.infrastructure.httpx.cliente_gateway_xubio import XubioClienteGateway
from src.use_cases.errors import ExternalServiceError


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"cliente_id": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.cliente_gateway_xubio.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway()
    assert gw.list() == [{"cliente_id": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"cliente_id": 2}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.cliente_gateway_xubio.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway()
    assert gw.list() == [{"cliente_id": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.cliente_gateway_xubio.request_with_token",
        fake_request,
    )
    gw = XubioClienteGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()
