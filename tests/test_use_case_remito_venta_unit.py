import pytest

from src.entities.remito_venta import RemitoVenta, TransaccionProductoItem
from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from src.infrastructure.memory.deposito_gateway_memory import InMemoryDepositoGateway
from src.infrastructure.memory.lista_precio_gateway_memory import (
    InMemoryListaPrecioGateway,
)
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway
from src.infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from src.use_cases import remito_venta


def _deps(cliente_gw, producto_gw, deposito_gw, lista_precio_gw):
    return remito_venta.RemitoDependencies(
        cliente_gateway=cliente_gw,
        producto_gateway=producto_gw,
        deposito_gateway=deposito_gw,
        lista_precio_gateway=lista_precio_gw,
    )


def test_list_get_update_delete_paths():
    gateway = InMemoryRemitoGateway()
    gateway.create({"clienteId": 1, "fecha": "2026-02-10"})

    listed = remito_venta.list_remitos(gateway)
    assert len(listed) == 1

    found = remito_venta.get_remito(gateway, 1)
    missing = remito_venta.get_remito(gateway, 999)
    assert found is not None
    assert missing is None

    deps = _deps(
        InMemoryClienteGateway(),
        InMemoryProductoGateway(),
        InMemoryDepositoGateway(),
        InMemoryListaPrecioGateway(),
    )
    deps.cliente_gateway.create({"nombre": "C1"})

    entity = RemitoVenta.from_dict({"clienteId": 1, "fecha": "2026-02-11"})
    updated = remito_venta.update_remito(gateway, 1, entity, deps)
    missing_updated = remito_venta.update_remito(gateway, 999, entity, deps)
    assert updated is not None
    assert missing_updated is None

    assert remito_venta.delete_remito(gateway, 1) is True
    assert remito_venta.delete_remito(gateway, 1) is False


def test_missing_cliente_and_lista_precio_errors():
    gateway = InMemoryRemitoGateway()
    cliente_gw = InMemoryClienteGateway()
    producto_gw = InMemoryProductoGateway()
    deposito_gw = InMemoryDepositoGateway()
    lista_precio_gw = InMemoryListaPrecioGateway()

    deps = _deps(cliente_gw, producto_gw, deposito_gw, lista_precio_gw)

    with pytest.raises(ValueError, match="clienteId es requerido"):
        remito_venta.create_remito(
            gateway,
            RemitoVenta.from_dict({"fecha": "2026-02-11"}),
            deps,
        )

    cliente_gw.create({"nombre": "C1"})
    with pytest.raises(ValueError, match="listaPrecioId 99 no encontrado"):
        remito_venta.create_remito(
            gateway,
            RemitoVenta.from_dict(
                {"clienteId": 1, "fecha": "2026-02-11", "listaPrecioId": 99}
            ),
            deps,
        )


def test_producto_item_validation_and_extractors():
    item = TransaccionProductoItem.from_dict({"cantidad": 1, "precio": 10})
    assert item is not None
    assert remito_venta._extract_producto_id(item) is None

    with pytest.raises(ValueError, match="productoId es requerido en item 0"):
        remito_venta._ensure_productos_exist(InMemoryProductoGateway(), [item])

    item_with_producto = TransaccionProductoItem.from_dict(
        {
            "cantidad": 1,
            "precio": 10,
            "producto": {"id": 5},
        }
    )
    assert item_with_producto is not None
    assert remito_venta._extract_producto_id(item_with_producto) == 5


def test_item_deposito_validation_and_extractors():
    deposito_gw = InMemoryDepositoGateway()

    item_with_deposito = TransaccionProductoItem.from_dict(
        {
            "cantidad": 1,
            "precio": 10,
            "deposito": {"ID": 3},
        }
    )
    assert item_with_deposito is not None
    assert remito_venta._extract_deposito_id(item_with_deposito) == 3

    with pytest.raises(ValueError, match="depositoId 3 no encontrado en item 0"):
        remito_venta._ensure_item_depositos_exist(deposito_gw, [item_with_deposito])

    deposito_gw.create({"nombre": "D1"})  # id 1
    item_with_deposito_id = TransaccionProductoItem.from_dict(
        {
            "cantidad": 1,
            "precio": 10,
            "deposito": {"id": 1},
        }
    )
    assert item_with_deposito_id is not None
    assert remito_venta._extract_deposito_id(item_with_deposito_id) == 1

