import os

from fastapi.testclient import TestClient

from src.infrastructure.fastapi.routers.remito import remito_create, remito_list
from src.infrastructure.fastapi.api import app as global_app
from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from src.infrastructure.memory.deposito_gateway_memory import InMemoryDepositoGateway
from src.infrastructure.memory.lista_precio_gateway_memory import (
    InMemoryListaPrecioGateway,
)
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway
from src.infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from src.interface_adapter.schemas.remito_venta import RemitoVentaPayload


def test_get_remitos_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway_provider.remito_gateway = InMemoryRemitoGateway()
    data = remito_list()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_write_blocked_when_is_prod_false():
    os.environ["IS_PROD"] = "false"
    gateway_provider.remito_gateway = InMemoryRemitoGateway()
    try:
        remito_create(body=_make_payload())
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 403
    else:
        raise AssertionError("Expected HTTPException 403")


def _make_payload():
    return RemitoVentaPayload(numeroRemito="R-1", clienteId=1, fecha="2026-02-09")


def test_remito_entity_validation():
    from src.entities.remito_venta import RemitoVenta

    try:
        RemitoVenta.from_dict({"fecha": "2026-13-40"})
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid fecha")


def test_remito_item_requires_positive_values():
    from src.entities.remito_venta import RemitoVenta

    try:
        remito = RemitoVenta.from_dict(
            {
                "clienteId": 1,
                "fecha": "2026-02-09",
                "transaccionProductoItem": [
                    {"cantidad": 0, "precio": 100},
                ],
            }
        )
        remito.validate()
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for non-positive cantidad")


def test_swagger_put_remito_requires_transaccion_id(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    client = TestClient(global_app)

    response = client.put(
        "/API/1.1/remitoVentaBean",
        json={"numeroRemito": "R-2", "clienteId": 1, "fecha": "2026-02-10"},
    )

    assert response.status_code == 400
    assert "transaccionId" in response.json()["detail"]


def test_swagger_put_remito_updates_existing_transaccion(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    remito_gateway = InMemoryRemitoGateway()
    remito_gateway.create({"numeroRemito": "R-1", "clienteId": 1, "fecha": "2026-02-09"})

    cliente_gateway = InMemoryClienteGateway()
    cliente_gateway.create({"nombre": "ACME"})

    gateway_provider.remito_gateway = remito_gateway
    gateway_provider.cliente_gateway = cliente_gateway
    gateway_provider.producto_gateway = InMemoryProductoGateway()
    gateway_provider.deposito_gateway = InMemoryDepositoGateway()
    gateway_provider.lista_precio_gateway = InMemoryListaPrecioGateway()

    client = TestClient(global_app)
    response = client.put(
        "/API/1.1/remitoVentaBean",
        json={
            "transaccionId": 1,
            "numeroRemito": "R-2",
            "clienteId": 1,
            "fecha": "2026-02-10",
        },
    )

    assert response.status_code == 200
    assert response.json()["transaccionId"] == 1
    assert response.json()["numeroRemito"] == "R-2"


def test_put_remito_with_path_rejects_mismatched_body_transaccion_id(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    remito_gateway = InMemoryRemitoGateway()
    remito_gateway.create({"numeroRemito": "R-1", "clienteId": 1, "fecha": "2026-02-09"})

    cliente_gateway = InMemoryClienteGateway()
    cliente_gateway.create({"nombre": "ACME"})

    gateway_provider.remito_gateway = remito_gateway
    gateway_provider.cliente_gateway = cliente_gateway
    gateway_provider.producto_gateway = InMemoryProductoGateway()
    gateway_provider.deposito_gateway = InMemoryDepositoGateway()
    gateway_provider.lista_precio_gateway = InMemoryListaPrecioGateway()

    client = TestClient(global_app)
    response = client.put(
        "/API/1.1/remitoVentaBean/1",
        json={
            "transaccionId": 2,
            "numeroRemito": "R-2",
            "clienteId": 1,
            "fecha": "2026-02-10",
        },
    )

    assert response.status_code == 400
    assert "coincidir con el path" in response.json()["detail"]
