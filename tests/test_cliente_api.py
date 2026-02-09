import os

from src.infrastructure.fastapi.api import cliente_list, cliente_create
from src.infrastructure.fastapi.api import app as global_app
from src.interface_adapter.schemas.cliente import ClientePayload


def test_get_clientes_returns_wrapper(app_fixture):
    os.environ["IS_PROD"] = "false"
    # Use fixture to keep test deterministic.
    global_app.cliente_gateway = app_fixture.cliente_gateway_fixture
    data = cliente_list()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_write_blocked_when_is_prod_false(monkeypatch, app_fixture):
    monkeypatch.setenv("IS_PROD", "false")
    global_app.cliente_gateway = app_fixture.cliente_gateway_fixture
    try:
        cliente_create(body=_make_payload())
    except Exception as exc:
        # FastAPI raises HTTPException for 403
        assert getattr(exc, "status_code", None) == 403
    else:
        raise AssertionError("Expected HTTPException 403")


def _make_payload():
    return ClientePayload(nombre="test")
