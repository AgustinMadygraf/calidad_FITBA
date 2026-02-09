"""
Path: src/use_cases/cliente.py
"""

from typing import List, Optional

from ..entities.cliente import Cliente
from ..interface_adapter.gateways.cliente_gateway import ClienteGateway


def list_clientes(gateway: ClienteGateway) -> List[Cliente]:
    items = gateway.list()
    return [Cliente.from_dict(x) for x in items]


def get_cliente(gateway: ClienteGateway, cliente_id: int) -> Optional[Cliente]:
    item = gateway.get(cliente_id)
    if item is None:
        return None
    return Cliente.from_dict(item)


def create_cliente(gateway: ClienteGateway, entity: Cliente) -> Cliente:
    created = gateway.create(entity.to_dict(exclude_none=True))
    return Cliente.from_dict(created)


def update_cliente(
    gateway: ClienteGateway, cliente_id: int, entity: Cliente
) -> Optional[Cliente]:
    updated = gateway.update(cliente_id, entity.to_dict(exclude_none=True))
    if updated is None:
        return None
    return Cliente.from_dict(updated)


def delete_cliente(gateway: ClienteGateway, cliente_id: int) -> bool:
    return gateway.delete(cliente_id)
