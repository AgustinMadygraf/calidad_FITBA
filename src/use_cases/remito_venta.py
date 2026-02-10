from typing import List, Optional

from ..entities.remito_venta import RemitoVenta
from ..use_cases.ports.cliente_gateway import ClienteGateway
from ..use_cases.ports.remito_gateway import RemitoGateway


def list_remitos(gateway: RemitoGateway) -> List[RemitoVenta]:
    items = gateway.list()
    return [RemitoVenta.from_dict(x) for x in items]


def get_remito(gateway: RemitoGateway, transaccion_id: int) -> Optional[RemitoVenta]:
    item = gateway.get(transaccion_id)
    if item is None:
        return None
    return RemitoVenta.from_dict(item)


def create_remito(
    gateway: RemitoGateway, entity: RemitoVenta, cliente_gateway: ClienteGateway
) -> RemitoVenta:
    entity.validate()
    _ensure_cliente_exists(cliente_gateway, entity.clienteId)
    created = gateway.create(entity.to_dict(exclude_none=True))
    return RemitoVenta.from_dict(created)


def update_remito(
    gateway: RemitoGateway,
    transaccion_id: int,
    entity: RemitoVenta,
    cliente_gateway: ClienteGateway,
) -> Optional[RemitoVenta]:
    entity.validate()
    _ensure_cliente_exists(cliente_gateway, entity.clienteId)
    updated = gateway.update(transaccion_id, entity.to_dict(exclude_none=True))
    if updated is None:
        return None
    return RemitoVenta.from_dict(updated)


def delete_remito(gateway: RemitoGateway, transaccion_id: int) -> bool:
    return gateway.delete(transaccion_id)


def _ensure_cliente_exists(
    gateway: ClienteGateway, cliente_id: Optional[int]
) -> None:
    if cliente_id is None:
        raise ValueError("clienteId es requerido")
    if gateway.get(cliente_id) is None:
        raise ValueError("clienteId no encontrado")
