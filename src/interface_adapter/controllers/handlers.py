from typing import Any, Dict, Optional

from ...entities.cliente import Cliente
from ...entities.remito_venta import RemitoVenta
from ...use_cases.ports.token_gateway import TokenGateway
from ...use_cases.ports.remito_gateway import RemitoGateway
from ...use_cases.ports.producto_gateway import ProductoGateway
from ...use_cases.ports.deposito_gateway import DepositoGateway
from ...use_cases.ports.lista_precio_gateway import ListaPrecioGateway
from ...interface_adapter.presenter import token_presenter
from ...use_cases import cliente, remito_venta, token_inspect
from ...use_cases.ports.cliente_gateway import ClienteGateway


def root() -> Dict[str, str]:
    return {"status": "ok", "message": "Xubio-like API"}


def health() -> Dict[str, str]:
    return {"status": "ok"}


def inspect_token(gateway: TokenGateway) -> Dict[str, Any]:
    status = token_inspect.execute(gateway)
    return token_presenter.present(status)


def list_clientes(gateway: ClienteGateway) -> Dict[str, Any]:
    items = cliente.list_clientes(gateway)
    return {"items": [x.to_dict(exclude_none=True) for x in items]}


def debug_clientes(gateway: ClienteGateway) -> Dict[str, Any]:
    items = cliente.list_clientes(gateway)
    sample = [x.to_dict(exclude_none=True) for x in items[:3]]
    return {"count": len(items), "sample": sample}


def list_remitos(gateway: RemitoGateway) -> Dict[str, Any]:
    items = remito_venta.list_remitos(gateway)
    return {"items": [x.to_dict(exclude_none=True) for x in items]}


def get_remito(gateway: RemitoGateway, transaccion_id: int) -> Optional[Dict[str, Any]]:
    entity = remito_venta.get_remito(gateway, transaccion_id)
    if entity is None:
        return None
    return entity.to_dict(exclude_none=True)


def create_remito(
    gateway: RemitoGateway,
    deps: remito_venta.RemitoDependencies,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    entity = RemitoVenta.from_dict(data)
    created = remito_venta.create_remito(gateway, entity, deps)
    return created.to_dict(exclude_none=True)


def update_remito(
    gateway: RemitoGateway,
    transaccion_id: int,
    deps: remito_venta.RemitoDependencies,
    data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    entity = RemitoVenta.from_dict(data)
    updated = remito_venta.update_remito(gateway, transaccion_id, entity, deps)
    if updated is None:
        return None
    return updated.to_dict(exclude_none=True)


def delete_remito(gateway: RemitoGateway, transaccion_id: int) -> bool:
    return remito_venta.delete_remito(gateway, transaccion_id)


def get_cliente(gateway: ClienteGateway, cliente_id: int) -> Optional[Dict[str, Any]]:
    entity = cliente.get_cliente(gateway, cliente_id)
    if entity is None:
        return None
    return entity.to_dict(exclude_none=True)


def list_productos(gateway: ProductoGateway) -> Dict[str, Any]:
    items = gateway.list()
    return {"items": items}


def get_producto(
    gateway: ProductoGateway, producto_id: int
) -> Optional[Dict[str, Any]]:
    return gateway.get(producto_id)


def list_depositos(gateway: DepositoGateway) -> Dict[str, Any]:
    items = gateway.list()
    return {"items": items}


def get_deposito(
    gateway: DepositoGateway, deposito_id: int
) -> Optional[Dict[str, Any]]:
    return gateway.get(deposito_id)


def list_lista_precios(gateway: ListaPrecioGateway) -> Dict[str, Any]:
    items = gateway.list()
    return {"items": items}


def get_lista_precio(
    gateway: ListaPrecioGateway, lista_precio_id: int
) -> Optional[Dict[str, Any]]:
    return gateway.get(lista_precio_id)


def create_cliente(gateway: ClienteGateway, data: Dict[str, Any]) -> Dict[str, Any]:
    entity = Cliente.from_dict(data)
    created = cliente.create_cliente(gateway, entity)
    return created.to_dict(exclude_none=True)


def update_cliente(
    gateway: ClienteGateway, cliente_id: int, data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    entity = Cliente.from_dict(data)
    updated = cliente.update_cliente(gateway, cliente_id, entity)
    if updated is None:
        return None
    return updated.to_dict(exclude_none=True)


def delete_cliente(gateway: ClienteGateway, cliente_id: int) -> bool:
    return cliente.delete_cliente(gateway, cliente_id)
