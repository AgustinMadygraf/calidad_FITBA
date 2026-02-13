from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ....interface_adapter.payload_validation import validate_lista_precio_payload
from ..gateway_provider import gateway_provider
from ..runtime_policy import ensure_write_allowed

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


@router.post(LISTA_PRECIO_BASE)
@router.post(LISTA_PRECIO_BASE_SLASH, include_in_schema=False)
def lista_precio_create(body: Dict[str, Any]) -> Dict[str, Any]:
    ensure_write_allowed()
    validated_body = validate_lista_precio_payload(body)
    return handlers.create_lista_precio(
        gateway_provider.lista_precio_gateway, validated_body
    )


@router.put(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@router.put(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_update(lista_precio_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
    ensure_write_allowed()
    validated_body = validate_lista_precio_payload(
        body, path_lista_precio_id=lista_precio_id
    )
    item = handlers.update_lista_precio(
        gateway_provider.lista_precio_gateway, lista_precio_id, validated_body
    )
    if item is None:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return item


@router.patch(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@router.patch(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_patch(lista_precio_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
    ensure_write_allowed()
    validated_body = validate_lista_precio_payload(
        body, path_lista_precio_id=lista_precio_id
    )
    item = handlers.patch_lista_precio(
        gateway_provider.lista_precio_gateway, lista_precio_id, validated_body
    )
    if item is None:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return item


@router.delete(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@router.delete(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_delete(lista_precio_id: int) -> Dict[str, Any]:
    ensure_write_allowed()
    ok = handlers.delete_lista_precio(
        gateway_provider.lista_precio_gateway, lista_precio_id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return {"status": "deleted", "listaPrecioID": lista_precio_id}
