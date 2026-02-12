import os

from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app as global_app
from src.infrastructure.fastapi.api import vendedor_list
from src.infrastructure.memory.vendedor_gateway_memory import InMemoryVendedorGateway
from src.use_cases.errors import ExternalServiceError


def test_get_vendedores_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    global_app.vendedor_gateway = InMemoryVendedorGateway()

    data = vendedor_list()

    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["items"][0]["vendedorId"] == 0


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
