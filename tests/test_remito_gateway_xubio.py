import httpx
import pytest

from src.infrastructure.httpx.remito_gateway_xubio import XubioRemitoGateway
from src.use_cases.errors import ExternalServiceError


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"transaccionId": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.remito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioRemitoGateway()
    assert gw.list() == [{"transaccionId": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"transaccionId": 2}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.remito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioRemitoGateway()
    assert gw.list() == [{"transaccionId": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.remito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioRemitoGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()
