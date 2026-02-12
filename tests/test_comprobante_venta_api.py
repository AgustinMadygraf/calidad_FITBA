import os

from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import (
    app as global_app,
)
from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.comprobante_venta import (
    comprobante_venta_get,
    comprobante_venta_list,
)
from src.infrastructure.memory.comprobante_venta_gateway_memory import (
    InMemoryComprobanteVentaGateway,
)
from src.use_cases.errors import ExternalServiceError


def test_get_comprobantes_venta_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway_provider.comprobante_venta_gateway = InMemoryComprobanteVentaGateway()

    data = comprobante_venta_list()

    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["items"][0]["transaccionid"] == 0


def test_get_comprobante_venta_by_id_returns_item():
    os.environ["IS_PROD"] = "false"
    gateway_provider.comprobante_venta_gateway = InMemoryComprobanteVentaGateway()

    item = comprobante_venta_get(0)

    assert item["transaccionid"] == 0
    assert item["nombre"] == "string"


def test_get_comprobante_venta_by_id_route_returns_404_when_missing(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    gateway_provider.comprobante_venta_gateway = InMemoryComprobanteVentaGateway()
    client = TestClient(global_app)

    response = client.get("/API/1.1/comprobanteVentaBean/999")

    assert response.status_code == 404


def test_get_comprobantes_venta_route_returns_502_on_gateway_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    gateway_provider.comprobante_venta_gateway = object()
    monkeypatch.setattr(
        "src.interface_adapter.controllers.handlers.list_comprobantes_venta",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ExternalServiceError("boom")),
    )
    client = TestClient(global_app)

    response = client.get("/API/1.1/comprobanteVentaBean")

    assert response.status_code == 502


def test_get_comprobante_venta_route_returns_502_on_gateway_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    gateway_provider.comprobante_venta_gateway = object()
    monkeypatch.setattr(
        "src.interface_adapter.controllers.handlers.get_comprobante_venta",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ExternalServiceError("boom")),
    )
    client = TestClient(global_app)

    response = client.get("/API/1.1/comprobanteVentaBean/1")

    assert response.status_code == 502
