from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ....interface_adapter.schemas.remito_venta import RemitoVentaPayload
from ....use_cases import remito_venta
from ..gateway_provider import gateway_provider
from ..remito_utils import resolve_remito_transaccion_id
from ..runtime_policy import ensure_write_allowed

router = APIRouter()

REMITO_BASE = "/API/1.1/remitoVentaBean"
REMITO_BASE_SLASH = "/API/1.1/remitoVentaBean/"


def _build_remito_dependencies() -> remito_venta.RemitoDependencies:
    return remito_venta.RemitoDependencies(
        cliente_gateway=gateway_provider.cliente_gateway,
        producto_gateway=gateway_provider.producto_gateway,
        deposito_gateway=gateway_provider.deposito_gateway,
        lista_precio_gateway=gateway_provider.lista_precio_gateway,
    )


@router.get(REMITO_BASE)
@router.get(REMITO_BASE_SLASH, include_in_schema=False)
def remito_list() -> Dict[str, Any]:
    return handlers.list_remitos(gateway_provider.remito_gateway)


@router.post(REMITO_BASE)
@router.post(REMITO_BASE_SLASH, include_in_schema=False)
def remito_create(body: RemitoVentaPayload) -> Dict[str, Any]:
    ensure_write_allowed()
    data = body.model_dump(exclude_none=True)
    deps = _build_remito_dependencies()
    return handlers.create_remito(gateway_provider.remito_gateway, deps, data)


@router.put(REMITO_BASE)
@router.put(REMITO_BASE_SLASH, include_in_schema=False)
def remito_update_by_body(body: RemitoVentaPayload) -> Dict[str, Any]:
    ensure_write_allowed()
    data = body.model_dump(exclude_none=True)
    transaccion_id = resolve_remito_transaccion_id(data)
    deps = _build_remito_dependencies()
    item = handlers.update_remito(
        gateway_provider.remito_gateway, transaccion_id, deps, data
    )
    if item is None:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return item


@router.get(f"{REMITO_BASE}/{{transaccion_id}}")
@router.get(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_get(transaccion_id: int) -> Dict[str, Any]:
    item = handlers.get_remito(gateway_provider.remito_gateway, transaccion_id)
    if item is None:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return item


@router.put(f"{REMITO_BASE}/{{transaccion_id}}")
@router.put(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
@router.patch(f"{REMITO_BASE}/{{transaccion_id}}")
@router.patch(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_update(transaccion_id: int, body: RemitoVentaPayload) -> Dict[str, Any]:
    ensure_write_allowed()
    data = body.model_dump(exclude_none=True)
    transaccion_id = resolve_remito_transaccion_id(
        data, path_transaccion_id=transaccion_id
    )
    deps = _build_remito_dependencies()
    item = handlers.update_remito(
        gateway_provider.remito_gateway, transaccion_id, deps, data
    )
    if item is None:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return item


@router.delete(f"{REMITO_BASE}/{{transaccion_id}}")
@router.delete(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_delete(transaccion_id: int) -> Dict[str, Any]:
    ensure_write_allowed()
    ok = handlers.delete_remito(gateway_provider.remito_gateway, transaccion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return {"status": "deleted", "transaccionId": transaccion_id}
