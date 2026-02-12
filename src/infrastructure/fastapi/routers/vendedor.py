from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ..gateway_provider import gateway_provider

router = APIRouter()

VENDEDOR_BASE = "/API/1.1/vendedorBean"
VENDEDOR_BASE_SLASH = "/API/1.1/vendedorBean/"


@router.get(VENDEDOR_BASE)
@router.get(VENDEDOR_BASE_SLASH, include_in_schema=False)
def vendedor_list() -> Dict[str, Any]:
    return handlers.list_vendedores(gateway_provider.vendedor_gateway)


@router.get(f"{VENDEDOR_BASE}/{{vendedor_id}}")
@router.get(f"{VENDEDOR_BASE}/{{vendedor_id}}/", include_in_schema=False)
def vendedor_get(vendedor_id: int) -> Dict[str, Any]:
    item = handlers.get_vendedor(gateway_provider.vendedor_gateway, vendedor_id)
    if item is None:
        raise HTTPException(status_code=404, detail="vendedor no encontrado")
    return item
