import os

from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app as global_app
from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.lista_precio import (
    lista_precio_get,
    lista_precio_list,
)
from src.infrastructure.memory.lista_precio_gateway_memory import (
    InMemoryListaPrecioGateway,
)


def test_get_lista_precios_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway = InMemoryListaPrecioGateway()
    gateway.create({"nombre": "LP Base"})
    gateway_provider.lista_precio_gateway = gateway

    data = lista_precio_list()

    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["items"][0]["listaPrecioID"] == 1


def test_get_lista_precio_by_id_returns_item():
    os.environ["IS_PROD"] = "false"
    gateway = InMemoryListaPrecioGateway()
    gateway.create({"nombre": "LP Base"})
    gateway_provider.lista_precio_gateway = gateway

    item = lista_precio_get(1)

    assert item["listaPrecioID"] == 1
    assert item["nombre"] == "LP Base"


def test_lista_precio_crud_routes_in_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    gateway = InMemoryListaPrecioGateway()
    gateway.create({"nombre": "LP Original"})
    gateway_provider.lista_precio_gateway = gateway
    client = TestClient(global_app)

    create_response = client.post(
        "/API/1.1/listaPrecioBean",
        json={"nombre": "LP Nueva"},
    )
    assert create_response.status_code == 200
    assert create_response.json()["listaPrecioID"] == 2

    update_response = client.put(
        "/API/1.1/listaPrecioBean/1",
        json={"nombre": "LP Actualizada"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["nombre"] == "LP Actualizada"

    patch_response = client.patch(
        "/API/1.1/listaPrecioBean/1",
        json={"descripcion": "Actualizada por PATCH"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["descripcion"] == "Actualizada por PATCH"

    delete_response = client.delete("/API/1.1/listaPrecioBean/2")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"

    get_deleted_response = client.get("/API/1.1/listaPrecioBean/2")
    assert get_deleted_response.status_code == 404
