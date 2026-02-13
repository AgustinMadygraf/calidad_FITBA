from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ....interface_adapter.payload_validation import validate_producto_payload
from ..gateway_provider import gateway_provider
from ..runtime_policy import ensure_write_allowed

router = APIRouter()

PRODUCTO_BASE = "/API/1.1/ProductoVentaBean"
PRODUCTO_BASE_SLASH = "/API/1.1/ProductoVentaBean/"
PRODUCTO_COMPRA_BASE = "/API/1.1/ProductoCompraBean"
PRODUCTO_COMPRA_BASE_SLASH = "/API/1.1/ProductoCompraBean/"
LEGACY_PRODUCTO_BASE = "/API/1.1/productoVentaBean"
LEGACY_PRODUCTO_BASE_SLASH = "/API/1.1/productoVentaBean/"
LEGACY_PRODUCTO_COMPRA_BASE = "/API/1.1/productoCompraBean"
LEGACY_PRODUCTO_COMPRA_BASE_SLASH = "/API/1.1/productoCompraBean/"


@router.get(PRODUCTO_BASE)
@router.get(PRODUCTO_BASE_SLASH, include_in_schema=False)
@router.get(LEGACY_PRODUCTO_BASE, include_in_schema=False)
@router.get(LEGACY_PRODUCTO_BASE_SLASH, include_in_schema=False)
def producto_list() -> Dict[str, Any]:
    return handlers.list_productos(gateway_provider.producto_gateway)


@router.get(f"{PRODUCTO_BASE}/{{producto_id}}")
@router.get(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@router.get(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@router.get(
    f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False
)
def producto_get(producto_id: int) -> Dict[str, Any]:
    item = handlers.get_producto(gateway_provider.producto_gateway, producto_id)
    if item is None:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return item


@router.post(PRODUCTO_BASE)
@router.post(PRODUCTO_BASE_SLASH, include_in_schema=False)
@router.post(LEGACY_PRODUCTO_BASE, include_in_schema=False)
@router.post(LEGACY_PRODUCTO_BASE_SLASH, include_in_schema=False)
def producto_create(body: Dict[str, Any]) -> Dict[str, Any]:
    ensure_write_allowed()
    validated_body = validate_producto_payload(body)
    return handlers.create_producto(gateway_provider.producto_gateway, validated_body)


@router.put(f"{PRODUCTO_BASE}/{{producto_id}}")
@router.put(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@router.patch(f"{PRODUCTO_BASE}/{{producto_id}}")
@router.patch(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@router.put(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@router.put(
    f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False
)
@router.patch(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@router.patch(
    f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False
)
def producto_update(producto_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
    ensure_write_allowed()
    validated_body = validate_producto_payload(
        body, path_producto_id=producto_id
    )
    item = handlers.update_producto(
        gateway_provider.producto_gateway, producto_id, validated_body
    )
    if item is None:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return item


@router.delete(f"{PRODUCTO_BASE}/{{producto_id}}")
@router.delete(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@router.delete(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@router.delete(
    f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False
)
def producto_delete(producto_id: int) -> Dict[str, Any]:
    ensure_write_allowed()
    ok = handlers.delete_producto(gateway_provider.producto_gateway, producto_id)
    if not ok:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return {"status": "deleted", "productoid": producto_id}


@router.get(PRODUCTO_COMPRA_BASE)
@router.get(PRODUCTO_COMPRA_BASE_SLASH, include_in_schema=False)
@router.get(LEGACY_PRODUCTO_COMPRA_BASE, include_in_schema=False)
@router.get(LEGACY_PRODUCTO_COMPRA_BASE_SLASH, include_in_schema=False)
def producto_compra_list() -> Dict[str, Any]:
    return handlers.list_productos(gateway_provider.producto_compra_gateway)


@router.get(f"{PRODUCTO_COMPRA_BASE}/{{producto_id}}")
@router.get(f"{PRODUCTO_COMPRA_BASE}/{{producto_id}}/", include_in_schema=False)
@router.get(
    f"{LEGACY_PRODUCTO_COMPRA_BASE}/{{producto_id}}", include_in_schema=False
)
@router.get(
    f"{LEGACY_PRODUCTO_COMPRA_BASE}/{{producto_id}}/", include_in_schema=False
)
def producto_compra_get(producto_id: int) -> Dict[str, Any]:
    item = handlers.get_producto(gateway_provider.producto_compra_gateway, producto_id)
    if item is None:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return item
