from dataclasses import dataclass
from typing import List, Optional

from ..entities.remito_venta import RemitoVenta, TransaccionProductoItem
from ..shared.id_mapping import first_non_none
from ..use_cases.ports.cliente_gateway import ClienteGateway
from ..use_cases.ports.producto_gateway import ProductoGateway
from ..use_cases.ports.deposito_gateway import DepositoGateway
from ..use_cases.ports.lista_precio_gateway import ListaPrecioGateway
from ..use_cases.ports.remito_gateway import RemitoGateway


@dataclass(frozen=True)
class RemitoDependencies:
    cliente_gateway: ClienteGateway
    producto_gateway: ProductoGateway
    deposito_gateway: DepositoGateway
    lista_precio_gateway: ListaPrecioGateway


def list_remitos(gateway: RemitoGateway) -> List[RemitoVenta]:
    items = gateway.list()
    return [RemitoVenta.from_dict(x) for x in items]


def get_remito(gateway: RemitoGateway, transaccion_id: int) -> Optional[RemitoVenta]:
    item = gateway.get(transaccion_id)
    if item is None:
        return None
    return RemitoVenta.from_dict(item)


def create_remito(
    gateway: RemitoGateway,
    entity: RemitoVenta,
    deps: RemitoDependencies,
) -> RemitoVenta:
    entity.validate()
    _ensure_cliente_exists(deps.cliente_gateway, entity.relaciones.clienteId)
    _ensure_lista_precio_exists(
        deps.lista_precio_gateway, entity.relaciones.listaPrecioId
    )
    _ensure_productos_exist(deps.producto_gateway, entity.transaccionProductoItem)
    _ensure_deposito_exists(deps.deposito_gateway, entity.relaciones.depositoId)
    _ensure_item_depositos_exist(deps.deposito_gateway, entity.transaccionProductoItem)
    created = gateway.create(entity.to_dict(exclude_none=True))
    return RemitoVenta.from_dict(created)


def update_remito(
    gateway: RemitoGateway,
    transaccion_id: int,
    entity: RemitoVenta,
    deps: RemitoDependencies,
) -> Optional[RemitoVenta]:
    entity.validate()
    _ensure_cliente_exists(deps.cliente_gateway, entity.relaciones.clienteId)
    _ensure_lista_precio_exists(
        deps.lista_precio_gateway, entity.relaciones.listaPrecioId
    )
    _ensure_productos_exist(deps.producto_gateway, entity.transaccionProductoItem)
    _ensure_deposito_exists(deps.deposito_gateway, entity.relaciones.depositoId)
    _ensure_item_depositos_exist(deps.deposito_gateway, entity.transaccionProductoItem)
    updated = gateway.update(transaccion_id, entity.to_dict(exclude_none=True))
    if updated is None:
        return None
    return RemitoVenta.from_dict(updated)


def delete_remito(gateway: RemitoGateway, transaccion_id: int) -> bool:
    return gateway.delete(transaccion_id)


def _ensure_cliente_exists(gateway: ClienteGateway, cliente_id: Optional[int]) -> None:
    if cliente_id is None:
        raise ValueError("clienteId es requerido")
    if gateway.get(cliente_id) is None:
        raise ValueError("clienteId no encontrado")


def _ensure_lista_precio_exists(
    gateway: ListaPrecioGateway, lista_precio_id: Optional[int]
) -> None:
    if lista_precio_id is None:
        return
    if gateway.get(lista_precio_id) is None:
        raise ValueError(f"listaPrecioId {lista_precio_id} no encontrado")


def _ensure_productos_exist(
    gateway: ProductoGateway, items: List[TransaccionProductoItem]
) -> None:
    if not items:
        return
    producto_ids: List[int] = []
    for idx, item in enumerate(items):
        producto_id = _extract_producto_id(item)
        if producto_id is None or producto_id <= 0:
            raise ValueError(f"productoId es requerido en item {idx}")
        producto_ids.append(producto_id)
    for producto_id in sorted(set(producto_ids)):
        if gateway.get(producto_id) is None:
            raise ValueError(f"productoId {producto_id} no encontrado")


def _extract_producto_id(item: TransaccionProductoItem) -> Optional[int]:
    producto = item.producto_ref.producto
    return first_non_none(
        item.producto_ref.productoid,
        item.producto_ref.productoId,
        producto.productoid if producto else None,
        producto.ID if producto else None,
        producto.id if producto else None,
    )


def _ensure_deposito_exists(
    gateway: DepositoGateway, deposito_id: Optional[int]
) -> None:
    if deposito_id is None:
        return
    if gateway.get(deposito_id) is None:
        raise ValueError(f"depositoId {deposito_id} no encontrado")


def _ensure_item_depositos_exist(
    gateway: DepositoGateway, items: List[TransaccionProductoItem]
) -> None:
    if not items:
        return
    for idx, item in enumerate(items):
        deposito_id = _extract_deposito_id(item)
        if deposito_id is None:
            continue
        if gateway.get(deposito_id) is None:
            raise ValueError(f"depositoId {deposito_id} no encontrado en item {idx}")


def _extract_deposito_id(item: TransaccionProductoItem) -> Optional[int]:
    if item.refs.deposito is None:
        return None
    return first_non_none(item.refs.deposito.ID, item.refs.deposito.id)
