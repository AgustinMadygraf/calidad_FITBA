import httpx
import pytest

import src.infrastructure.httpx.deposito_gateway_xubio as deposito_gateway
from src.infrastructure.httpx.deposito_gateway_xubio import XubioDepositoGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    deposito_gateway._GLOBAL_LIST_CACHE = None
    yield
    deposito_gateway._GLOBAL_LIST_CACHE = None


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"id": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.deposito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioDepositoGateway()
    assert gw.list() == [{"id": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"id": 2}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.deposito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioDepositoGateway()
    assert gw.list() == [{"id": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.deposito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioDepositoGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_get_falls_back_to_list_on_5xx(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/depositos/9"):
            return httpx.Response(500, text="boom")
        if url.endswith("/depositos"):
            return httpx.Response(200, json=[{"id": 9}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.deposito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioDepositoGateway()
    assert gw.get(9) == {"id": 9}


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"id": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.deposito_gateway_xubio.request_with_token", fake_request
    )
    gw = XubioDepositoGateway(list_cache_ttl=60)
    assert gw.list() == [{"id": 1}]
    assert gw.list() == [{"id": 1}]
    assert calls["count"] == 1
