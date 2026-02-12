from fastapi.testclient import TestClient

from src.infrastructure.fastapi import deps
from src.infrastructure.fastapi.api import app
from src.infrastructure.httpx.cliente_gateway_xubio import XubioClienteGateway
from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from src.infrastructure.memory.lista_precio_gateway_memory import (
    InMemoryListaPrecioGateway,
)
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway


def test_non_prod_builds_xubio_gateway_with_read_cache(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")

    gateway = deps.get_cliente_gateway()

    assert isinstance(gateway, XubioClienteGateway)
    assert gateway._list_cache_ttl > 0


def test_prod_builds_xubio_gateway_without_read_cache(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")

    gateway = deps.get_cliente_gateway()

    assert isinstance(gateway, XubioClienteGateway)
    assert gateway._list_cache_ttl == 0


def test_patch_routes_are_registered():
    patch_paths = {
        route.path
        for route in app.routes
        if hasattr(route, "methods") and "PATCH" in route.methods
    }
    assert "/API/1.1/clienteBean/{cliente_id}" in patch_paths
    assert "/API/1.1/remitoVentaBean/{transaccion_id}" in patch_paths
    assert "/API/1.1/ProductoVentaBean/{producto_id}" in patch_paths


def test_producto_contract_routes_are_registered():
    route_paths = {
        route.path
        for route in app.routes
        if hasattr(route, "methods")
    }
    assert "/API/1.1/ProductoVentaBean" in route_paths
    assert "/API/1.1/ProductoVentaBean/{producto_id}" in route_paths
    assert "/API/1.1/ProductoCompraBean" in route_paths


def test_patch_is_forbidden_in_non_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    client = TestClient(app)

    response = client.patch("/API/1.1/clienteBean/1", json={})

    assert response.status_code == 403


def test_patch_is_enabled_in_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(app, "cliente_gateway", InMemoryClienteGateway(), raising=False)
    monkeypatch.setattr(
        app, "lista_precio_gateway", InMemoryListaPrecioGateway(), raising=False
    )
    client = TestClient(app)

    response = client.patch("/API/1.1/clienteBean/1", json={})

    assert response.status_code == 404


def test_producto_mutations_forbidden_in_non_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    client = TestClient(app)

    response = client.post("/API/1.1/ProductoVentaBean", json={})

    assert response.status_code == 403


def test_producto_create_enabled_in_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(app, "producto_gateway", InMemoryProductoGateway(), raising=False)
    client = TestClient(app)

    response = client.post("/API/1.1/ProductoVentaBean", json={"nombre": "P1"})

    assert response.status_code == 200
    assert response.json()["productoid"] == 1


def test_legacy_lowercase_producto_route_still_works(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    gateway = InMemoryProductoGateway()
    gateway.create({"nombre": "P1"})
    monkeypatch.setattr(app, "producto_gateway", gateway, raising=False)
    client = TestClient(app)

    response = client.get("/API/1.1/productoVentaBean/")

    assert response.status_code == 200
    assert response.json()["items"][0]["productoid"] == 1


def test_non_prod_forbids_mutation_without_route(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    client = TestClient(app)

    response = client.post("/API/1.1/monedaBean", json={})

    assert response.status_code == 403


def test_prod_keeps_405_for_unknown_mutation_route(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    client = TestClient(app)

    response = client.post("/API/1.1/monedaBean", json={})

    assert response.status_code == 405
