from src.entities.remito_venta import RemitoVenta
from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from src.infrastructure.memory.deposito_gateway_memory import InMemoryDepositoGateway
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway
from src.infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from src.use_cases import remito_venta


def _make_entity(cliente_id: int, producto_id: int) -> RemitoVenta:
    return RemitoVenta.from_dict(
        {
            "clienteId": cliente_id,
            "fecha": "2026-02-09",
            "transaccionProductoItem": [
                {
                    "productoId": producto_id,
                    "cantidad": 1,
                    "precio": 100,
                }
            ],
        }
    )


def test_create_remito_rejects_missing_producto():
    remito_gateway = InMemoryRemitoGateway()
    cliente_gateway = InMemoryClienteGateway()
    producto_gateway = InMemoryProductoGateway()
    deposito_gateway = InMemoryDepositoGateway()
    cliente = cliente_gateway.create({"nombre": "Cliente OK"})
    entity = _make_entity(cliente["cliente_id"], 999)
    deps = remito_venta.RemitoDependencies(
        cliente_gateway=cliente_gateway,
        producto_gateway=producto_gateway,
        deposito_gateway=deposito_gateway,
    )
    try:
        remito_venta.create_remito(remito_gateway, entity, deps)
    except ValueError as exc:
        assert "productoId" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing producto")


def test_create_remito_accepts_existing_producto():
    remito_gateway = InMemoryRemitoGateway()
    cliente_gateway = InMemoryClienteGateway()
    producto_gateway = InMemoryProductoGateway()
    deposito_gateway = InMemoryDepositoGateway()
    cliente = cliente_gateway.create({"nombre": "Cliente OK"})
    producto = producto_gateway.create({"nombre": "Producto OK"})
    entity = _make_entity(cliente["cliente_id"], producto["productoid"])
    deps = remito_venta.RemitoDependencies(
        cliente_gateway=cliente_gateway,
        producto_gateway=producto_gateway,
        deposito_gateway=deposito_gateway,
    )
    created = remito_venta.create_remito(remito_gateway, entity, deps)
    assert created.transaccionId is not None
