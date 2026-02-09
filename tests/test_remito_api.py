import os

from src.infrastructure.fastapi.api import remito_list, remito_create
from src.infrastructure.fastapi.api import app as global_app
from src.infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from src.interface_adapter.schemas.remito_venta import RemitoVentaPayload


def test_get_remitos_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    global_app.remito_gateway = InMemoryRemitoGateway()
    data = remito_list()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_write_blocked_when_is_prod_false():
    os.environ["IS_PROD"] = "false"
    global_app.remito_gateway = InMemoryRemitoGateway()
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
