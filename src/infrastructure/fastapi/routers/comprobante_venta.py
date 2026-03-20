from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ..gateway_provider import gateway_provider

router = APIRouter()

COMPROBANTE_VENTA_BASE = "/API/1.1/comprobanteVentaBean"
COMPROBANTE_VENTA_BASE_SLASH = "/API/1.1/comprobanteVentaBean/"


@router.get(COMPROBANTE_VENTA_BASE)
@router.get(COMPROBANTE_VENTA_BASE_SLASH, include_in_schema=False)
def comprobante_venta_list() -> Dict[str, Any]:
    return handlers.list_comprobantes_venta(gateway_provider.comprobante_venta_gateway)


@router.get(f"{COMPROBANTE_VENTA_BASE}/{{id}}")
@router.get(f"{COMPROBANTE_VENTA_BASE}/{{id}}/", include_in_schema=False)
def comprobante_venta_get(id: int) -> Dict[str, Any]:
    item = handlers.get_comprobante_venta(
        gateway_provider.comprobante_venta_gateway, id
    )
    if item is None:
        raise HTTPException(
            status_code=404, detail="comprobante de venta no encontrado"
        )
    return item
