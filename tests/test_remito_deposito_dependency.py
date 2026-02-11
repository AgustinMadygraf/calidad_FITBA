from src.entities.remito_venta import RemitoVenta
from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from src.infrastructure.memory.deposito_gateway_memory import InMemoryDepositoGateway
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway
from src.infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from src.use_cases import remito_venta


def _make_entity(cliente_id: int, deposito_id: int) -> RemitoVenta:
    return RemitoVenta.from_dict(
        {
            "clienteId": cliente_id,
            "depositoId": deposito_id,
            "fecha": "2026-02-09",
        }
    )


def test_create_remito_rejects_missing_deposito():
    remito_gateway = InMemoryRemitoGateway()
    cliente_gateway = InMemoryClienteGateway()
    producto_gateway = InMemoryProductoGateway()
    deposito_gateway = InMemoryDepositoGateway()
    cliente = cliente_gateway.create({"nombre": "Cliente OK"})
    entity = _make_entity(cliente["cliente_id"], 999)
    try:
        remito_venta.create_remito(
            remito_gateway, entity, cliente_gateway, producto_gateway, deposito_gateway
        )
    except ValueError as exc:
        assert "depositoId" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing deposito")


def test_create_remito_accepts_existing_deposito():
    remito_gateway = InMemoryRemitoGateway()
    cliente_gateway = InMemoryClienteGateway()
    producto_gateway = InMemoryProductoGateway()
    deposito_gateway = InMemoryDepositoGateway()
    cliente = cliente_gateway.create({"nombre": "Cliente OK"})
    deposito = deposito_gateway.create({"nombre": "Deposito OK"})
    entity = _make_entity(cliente["cliente_id"], deposito["id"])
    created = remito_venta.create_remito(
        remito_gateway, entity, cliente_gateway, producto_gateway, deposito_gateway
    )
    assert created.transaccionId is not None
