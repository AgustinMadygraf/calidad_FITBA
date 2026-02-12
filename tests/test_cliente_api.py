import os

from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.cliente import cliente_create, cliente_list
from src.interface_adapter.schemas.cliente import ClientePayload


def test_get_clientes_returns_wrapper(app_fixture):
    os.environ["IS_PROD"] = "false"
    gateway_provider.cliente_gateway = app_fixture.cliente_gateway_fixture
    data = cliente_list()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_write_blocked_when_is_prod_false(monkeypatch, app_fixture):
    monkeypatch.setenv("IS_PROD", "false")
    gateway_provider.cliente_gateway = app_fixture.cliente_gateway_fixture
    try:
        cliente_create(body=_make_payload())
    except Exception as exc:
        # FastAPI raises HTTPException for 403
        assert getattr(exc, "status_code", None) == 403
    else:
        raise AssertionError("Expected HTTPException 403")


def _make_payload():
    return ClientePayload(nombre="test")
