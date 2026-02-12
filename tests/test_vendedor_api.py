import os

from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app as global_app
from src.infrastructure.fastapi.api import vendedor_get, vendedor_list
from src.infrastructure.memory.vendedor_gateway_memory import InMemoryVendedorGateway
from src.use_cases.errors import ExternalServiceError


def test_get_vendedores_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    global_app.vendedor_gateway = InMemoryVendedorGateway()

    data = vendedor_list()

    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["items"][0]["vendedorId"] == 0


def test_get_vendedor_by_id_returns_item():
    os.environ["IS_PROD"] = "false"
    global_app.vendedor_gateway = InMemoryVendedorGateway()

    item = vendedor_get(0)

    assert item["vendedorId"] == 0
    assert item["nombre"] == "string"


def test_get_vendedor_by_id_route_returns_404_when_missing(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    global_app.vendedor_gateway = InMemoryVendedorGateway()
    client = TestClient(global_app)

    response = client.get("/API/1.1/vendedorBean/999")

    assert response.status_code == 404


def test_get_vendedores_route_returns_502_on_gateway_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    monkeypatch.setattr(global_app, "vendedor_gateway", object(), raising=False)
    monkeypatch.setattr(
        "src.interface_adapter.controllers.handlers.list_vendedores",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ExternalServiceError("boom")),
    )
    client = TestClient(global_app)

    response = client.get("/API/1.1/vendedorBean")

    assert response.status_code == 502


def test_get_vendedor_route_returns_502_on_gateway_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    monkeypatch.setattr(global_app, "vendedor_gateway", object(), raising=False)
    monkeypatch.setattr(
        "src.interface_adapter.controllers.handlers.get_vendedor",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ExternalServiceError("boom")),
    )
    client = TestClient(global_app)

    response = client.get("/API/1.1/vendedorBean/1")

    assert response.status_code == 502
