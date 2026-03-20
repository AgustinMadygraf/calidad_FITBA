from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app
from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.memory.lista_precio_gateway_memory import (
    InMemoryListaPrecioGateway,
)
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway


def test_producto_create_keeps_unknown_payload_fields(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    gateway_provider.producto_gateway = InMemoryProductoGateway()
    client = TestClient(app)

    payload = {
        "nombre": "P1",
        "codigo": "COD-1",
        "meta": {"origen": "cli", "activo": 1},
        "atributos": [{"k": "color", "v": "rojo"}],
    }

    response = client.post("/API/1.1/ProductoVentaBean", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["productoid"] == 1
    assert body["nombre"] == "P1"
    assert body["codigo"] == "COD-1"
    assert body["meta"] == payload["meta"]
    assert body["atributos"] == payload["atributos"]


def test_producto_update_rejects_mismatched_body_id(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    gateway = InMemoryProductoGateway()
    gateway.create({"nombre": "Base"})
    gateway_provider.producto_gateway = gateway
    client = TestClient(app)

    response = client.put(
        "/API/1.1/ProductoVentaBean/1",
        json={"productoid": 2, "nombre": "Cambio"},
    )

    assert response.status_code == 400
    assert "coincidir con path" in response.json()["detail"]


def test_producto_create_rejects_inconsistent_id_aliases(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    gateway_provider.producto_gateway = InMemoryProductoGateway()
    client = TestClient(app)

    response = client.post(
        "/API/1.1/ProductoVentaBean",
        json={"productoid": 1, "productoId": 2},
    )

    assert response.status_code == 400
    assert "IDs inconsistentes" in response.json()["detail"]


def test_lista_precio_update_keeps_unknown_payload_fields(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    gateway = InMemoryListaPrecioGateway()
    gateway.create({"nombre": "LP Base"})
    gateway_provider.lista_precio_gateway = gateway
    client = TestClient(app)

    payload = {
        "ID": 1,
        "descripcion": "Actualizada",
        "customFlags": {"publica": True},
    }
    response = client.put("/API/1.1/listaPrecioBean/1", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["listaPrecioID"] == 1
    assert body["descripcion"] == "Actualizada"
    assert body["customFlags"] == payload["customFlags"]


def test_lista_precio_patch_rejects_mismatched_body_id(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    gateway = InMemoryListaPrecioGateway()
    gateway.create({"nombre": "LP Base"})
    gateway_provider.lista_precio_gateway = gateway
    client = TestClient(app)

    response = client.patch("/API/1.1/listaPrecioBean/1", json={"listaPrecioID": 2})

    assert response.status_code == 400
    assert "coincidir con path" in response.json()["detail"]


def test_lista_precio_patch_rejects_invalid_id_type(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    gateway = InMemoryListaPrecioGateway()
    gateway.create({"nombre": "LP Base"})
    gateway_provider.lista_precio_gateway = gateway
    client = TestClient(app)

    response = client.patch("/API/1.1/listaPrecioBean/1", json={"ID": "abc"})

    assert response.status_code == 400
    assert "payload lista de precio invalido" in response.json()["detail"]
