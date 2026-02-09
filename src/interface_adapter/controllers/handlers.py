from typing import Any, Dict, Optional

from ...interface_adapter.gateways.cliente_gateway import ClienteGateway
from ...interface_adapter.gateways.token_gateway import TokenGateway
from ...interface_adapter.presenter import token_presenter
from ...use_cases import cliente, token_inspect


def root() -> Dict[str, str]:
    return {"status": "ok", "message": "Xubio-like API"}


def health() -> Dict[str, str]:
    return {"status": "ok"}


def terminal_execute(command: str) -> Dict[str, Any]:
    return {"status": "stub", "echo": command}


def sync_pull_product(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"status": "stub", "action": "pull", "entity": "product", "payload": payload}


def sync_push_product(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"status": "stub", "action": "push", "entity": "product", "payload": payload}


def inspect_token(gateway: TokenGateway) -> Dict[str, Any]:
    status = token_inspect.execute(gateway)
    return token_presenter.present(status)


def list_clientes(gateway: ClienteGateway) -> Dict[str, Any]:
    items = cliente.list_clientes(gateway)
    return {"items": items}


def get_cliente(gateway: ClienteGateway, cliente_id: int) -> Optional[Dict[str, Any]]:
    return cliente.get_cliente(gateway, cliente_id)


def create_cliente(gateway: ClienteGateway, data: Dict[str, Any]) -> Dict[str, Any]:
    return cliente.create_cliente(gateway, data)


def update_cliente(
    gateway: ClienteGateway, cliente_id: int, data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    return cliente.update_cliente(gateway, cliente_id, data)


def delete_cliente(gateway: ClienteGateway, cliente_id: int) -> bool:
    return cliente.delete_cliente(gateway, cliente_id)
