import pytest

from src.entities.cliente import Cliente
from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from src.infrastructure.memory.lista_precio_gateway_memory import (
    InMemoryListaPrecioGateway,
)
from src.use_cases import cliente


def _deps(lista_precio_gateway):
    return cliente.ClienteDependencies(lista_precio_gateway=lista_precio_gateway)


def test_list_and_get_cliente():
    gateway = InMemoryClienteGateway()
    gateway.create({"nombre": "ACME"})

    items = cliente.list_clientes(gateway)
    assert len(items) == 1
    assert items[0].identidad.nombre == "ACME"

    found = cliente.get_cliente(gateway, 1)
    missing = cliente.get_cliente(gateway, 99)
    assert found is not None
    assert found.identidad.nombre == "ACME"
    assert missing is None


def test_create_cliente_without_lista_precio_reference():
    cliente_gateway = InMemoryClienteGateway()
    lista_precio_gateway = InMemoryListaPrecioGateway()
    entity = Cliente.from_dict({"nombre": "A"})

    created = cliente.create_cliente(cliente_gateway, entity, _deps(lista_precio_gateway))

    assert created.cliente_id == 1
    assert created.identidad.nombre == "A"


def test_create_cliente_with_valid_lista_precio():
    cliente_gateway = InMemoryClienteGateway()
    lista_precio_gateway = InMemoryListaPrecioGateway()
    lista_precio_gateway.create({"nombre": "LP1"})

    entity = Cliente.from_dict({"nombre": "A", "listaPrecioVenta": {"ID": 1}})
    created = cliente.create_cliente(cliente_gateway, entity, _deps(lista_precio_gateway))

    assert created.cliente_id == 1
    assert created.cuentas.listaPrecioVenta is not None
    assert created.cuentas.listaPrecioVenta.ID == 1


def test_create_cliente_rejects_invalid_lista_precio_reference():
    cliente_gateway = InMemoryClienteGateway()
    lista_precio_gateway = InMemoryListaPrecioGateway()

    invalid_entity = Cliente.from_dict(
        {"nombre": "A", "listaPrecioVenta": {"nombre": "sin-id"}}
    )
    with pytest.raises(ValueError, match="listaPrecioVenta debe incluir ID/id valido"):
        cliente.create_cliente(cliente_gateway, invalid_entity, _deps(lista_precio_gateway))

    missing_entity = Cliente.from_dict({"nombre": "A", "listaPrecioVenta": {"ID": 99}})
    with pytest.raises(ValueError, match="listaPrecioId 99 no encontrado"):
        cliente.create_cliente(cliente_gateway, missing_entity, _deps(lista_precio_gateway))


def test_update_cliente_behaviour():
    cliente_gateway = InMemoryClienteGateway()
    lista_precio_gateway = InMemoryListaPrecioGateway()
    lista_precio_gateway.create({"nombre": "LP1"})

    cliente_gateway.create({"nombre": "Original"})
    entity = Cliente.from_dict(
        {"nombre": "Actualizado", "listaPrecioVenta": {"id": 1}}
    )
    updated = cliente.update_cliente(cliente_gateway, 1, entity, _deps(lista_precio_gateway))
    assert updated is not None
    assert updated.identidad.nombre == "Actualizado"

    missing = cliente.update_cliente(cliente_gateway, 999, entity, _deps(lista_precio_gateway))
    assert missing is None


def test_update_cliente_prefers_id_from_id_or_ID():
    cliente_gateway = InMemoryClienteGateway()
    lista_precio_gateway = InMemoryListaPrecioGateway()
    lista_precio_gateway.create({"nombre": "LP1"})
    cliente_gateway.create({"nombre": "Original"})

    entity = Cliente.from_dict(
        {"nombre": "A", "listaPrecioVenta": {"ID": 1, "id": 999}}
    )
    updated = cliente.update_cliente(cliente_gateway, 1, entity, _deps(lista_precio_gateway))
    assert updated is not None
    assert updated.cuentas.listaPrecioVenta is not None
    assert updated.cuentas.listaPrecioVenta.ID == 1


def test_delete_cliente_proxy():
    gateway = InMemoryClienteGateway()
    gateway.create({"nombre": "A"})

    assert cliente.delete_cliente(gateway, 1) is True
    assert cliente.delete_cliente(gateway, 1) is False

