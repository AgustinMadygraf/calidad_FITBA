import httpx
import pytest

import src.infrastructure.httpx.circuito_contable_gateway_xubio as circuito_gateway
from src.infrastructure.httpx.circuito_contable_gateway_xubio import (
    XubioCircuitoContableGateway,
)
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    circuito_gateway._GLOBAL_LIST_CACHE.clear()
    yield
    circuito_gateway._GLOBAL_LIST_CACHE.clear()


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(
            200,
            json={
                "items": [
                    {"circuitoContable_id": 1, "codigo": "CC1", "nombre": "Circuito 1"}
                ]
            },
        )

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCircuitoContableGateway()
    assert gw.list() == [
        {"circuitoContable_id": 1, "codigo": "CC1", "nombre": "Circuito 1"}
    ]


def test_get_reads_from_list_only(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/circuitoContableBean/1"):
            raise AssertionError(
                "No debe llamar al endpoint detalle de circuito contable"
            )
        if url.endswith("/circuitoContableBean"):
            return httpx.Response(
                200,
                json=[{"circuitoContable_id": 1, "codigo": "CC1", "nombre": "Circuito 1"}],
            )
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCircuitoContableGateway()
    assert gw.get(1) == {"circuitoContable_id": 1, "codigo": "CC1", "nombre": "Circuito 1"}


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioCircuitoContableGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()
