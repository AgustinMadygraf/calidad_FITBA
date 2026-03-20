from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ..gateway_provider import gateway_provider

router = APIRouter()

CLIENTE_BASE = "/API/1.1/clienteBean"
CLIENTE_BASE_SLASH = "/API/1.1/clienteBean/"


@router.get(CLIENTE_BASE)
@router.get(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_list() -> Dict[str, Any]:
    return handlers.list_clientes(gateway_provider.cliente_gateway)


@router.get(f"{CLIENTE_BASE}/{{cliente_id}}")
@router.get(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_get(cliente_id: int) -> Dict[str, Any]:
    item = handlers.get_cliente(gateway_provider.cliente_gateway, cliente_id)
    if item is None:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return item

