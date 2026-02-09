"""
Path: src/use_cases/cliente.py
"""

from typing import Any, Dict, List, Optional

from ..interface_adapter.gateways.cliente_gateway import ClienteGateway


def list_clientes(gateway: ClienteGateway) -> List[Dict[str, Any]]:
    return gateway.list()


def get_cliente(gateway: ClienteGateway, cliente_id: int) -> Optional[Dict[str, Any]]:
    return gateway.get(cliente_id)


def create_cliente(gateway: ClienteGateway, data: Dict[str, Any]) -> Dict[str, Any]:
    return gateway.create(data)


def update_cliente(
    gateway: ClienteGateway, cliente_id: int, data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    return gateway.update(cliente_id, data)


def delete_cliente(gateway: ClienteGateway, cliente_id: int) -> bool:
    return gateway.delete(cliente_id)
