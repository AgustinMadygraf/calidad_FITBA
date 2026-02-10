from src.entities.remito_venta import RemitoVenta
from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from src.infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from src.use_cases import remito_venta


def _make_entity(cliente_id: int) -> RemitoVenta:
    return RemitoVenta.from_dict({"clienteId": cliente_id, "fecha": "2026-02-09"})


def test_create_remito_rejects_missing_cliente():
    remito_gateway = InMemoryRemitoGateway()
    cliente_gateway = InMemoryClienteGateway()
    entity = _make_entity(999)
    try:
        remito_venta.create_remito(remito_gateway, entity, cliente_gateway)
    except ValueError as exc:
        assert "clienteId" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing cliente")


def test_create_remito_accepts_existing_cliente():
    remito_gateway = InMemoryRemitoGateway()
    cliente_gateway = InMemoryClienteGateway()
    cliente = cliente_gateway.create({"nombre": "Cliente OK"})
    entity = _make_entity(cliente["cliente_id"])
    created = remito_venta.create_remito(remito_gateway, entity, cliente_gateway)
    assert created.transaccionId is not None
