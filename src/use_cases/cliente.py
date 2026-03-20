"""
Path: src/use_cases/cliente.py
"""

from dataclasses import dataclass
from typing import List, Optional

from ..entities.cliente import Cliente
from ..entities.common import SimpleItem
from ..shared.id_mapping import first_non_none
from ..use_cases.ports.cliente_gateway import ClienteGateway
from ..use_cases.ports.lista_precio_gateway import ListaPrecioGateway


@dataclass(frozen=True)
class ClienteDependencies:
    lista_precio_gateway: ListaPrecioGateway


def list_clientes(gateway: ClienteGateway) -> List[Cliente]:
    items = gateway.list()
    return [Cliente.from_dict(x) for x in items]


def get_cliente(gateway: ClienteGateway, cliente_id: int) -> Optional[Cliente]:
    item = gateway.get(cliente_id)
    if item is None:
        return None
    return Cliente.from_dict(item)


def create_cliente(
    gateway: ClienteGateway, entity: Cliente, deps: ClienteDependencies
) -> Cliente:
    _ensure_lista_precio_exists(
        deps.lista_precio_gateway, entity.cuentas.listaPrecioVenta
    )
    created = gateway.create(entity.to_dict(exclude_none=True))
    return Cliente.from_dict(created)


def update_cliente(
    gateway: ClienteGateway,
    cliente_id: int,
    entity: Cliente,
    deps: ClienteDependencies,
) -> Optional[Cliente]:
    _ensure_lista_precio_exists(
        deps.lista_precio_gateway, entity.cuentas.listaPrecioVenta
    )
    updated = gateway.update(cliente_id, entity.to_dict(exclude_none=True))
    if updated is None:
        return None
    return Cliente.from_dict(updated)


def delete_cliente(gateway: ClienteGateway, cliente_id: int) -> bool:
    return gateway.delete(cliente_id)


def _ensure_lista_precio_exists(
    gateway: ListaPrecioGateway, lista_precio: Optional[SimpleItem]
) -> None:
    if lista_precio is None:
        return
    lista_precio_id = _extract_lista_precio_id(lista_precio)
    if lista_precio_id is None or lista_precio_id <= 0:
        raise ValueError("listaPrecioVenta debe incluir ID/id valido")
    if gateway.get(lista_precio_id) is None:
        raise ValueError(f"listaPrecioId {lista_precio_id} no encontrado")


def _extract_lista_precio_id(lista_precio: SimpleItem) -> Optional[int]:
    return first_non_none(lista_precio.ID, lista_precio.id)
