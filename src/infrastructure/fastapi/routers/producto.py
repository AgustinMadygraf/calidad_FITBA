from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ..gateway_provider import gateway_provider

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
