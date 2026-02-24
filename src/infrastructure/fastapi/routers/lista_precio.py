from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ..gateway_provider import gateway_provider

router = APIRouter()

LISTA_PRECIO_BASE = "/API/1.1/listaPrecioBean"
LISTA_PRECIO_BASE_SLASH = "/API/1.1/listaPrecioBean/"


@router.get(LISTA_PRECIO_BASE)
@router.get(LISTA_PRECIO_BASE_SLASH, include_in_schema=False)
def lista_precio_list() -> Dict[str, Any]:
    return handlers.list_lista_precios(gateway_provider.lista_precio_gateway)


@router.get(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@router.get(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_get(lista_precio_id: int) -> Dict[str, Any]:
    item = handlers.get_lista_precio(
        gateway_provider.lista_precio_gateway, lista_precio_id
    )
    if item is None:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return item

