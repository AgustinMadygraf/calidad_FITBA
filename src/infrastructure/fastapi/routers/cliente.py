from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ....interface_adapter.schemas.cliente import ClientePayload
from ....use_cases import cliente
from ..gateway_provider import gateway_provider
from ..runtime_policy import ensure_debug_allowed, ensure_write_allowed

router = APIRouter()

CLIENTE_BASE = "/API/1.1/clienteBean"
CLIENTE_BASE_SLASH = "/API/1.1/clienteBean/"


@router.get(CLIENTE_BASE)
@router.get(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_list() -> Dict[str, Any]:
    return handlers.list_clientes(gateway_provider.cliente_gateway)


@router.get("/debug/clienteBean")
def cliente_list_debug() -> Dict[str, Any]:
    ensure_debug_allowed()
    return handlers.debug_clientes(gateway_provider.cliente_gateway)


@router.post(CLIENTE_BASE)
@router.post(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_create(body: ClientePayload) -> Dict[str, Any]:
    ensure_write_allowed()
    data = body.model_dump(exclude_none=True)
    deps = cliente.ClienteDependencies(
        lista_precio_gateway=gateway_provider.lista_precio_gateway
    )
    return handlers.create_cliente(gateway_provider.cliente_gateway, deps, data)


@router.get(f"{CLIENTE_BASE}/{{cliente_id}}")
@router.get(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_get(cliente_id: int) -> Dict[str, Any]:
    item = handlers.get_cliente(gateway_provider.cliente_gateway, cliente_id)
    if item is None:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return item


@router.put(f"{CLIENTE_BASE}/{{cliente_id}}")
@router.put(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
@router.patch(f"{CLIENTE_BASE}/{{cliente_id}}")
@router.patch(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_update(cliente_id: int, body: ClientePayload) -> Dict[str, Any]:
    ensure_write_allowed()
    data = body.model_dump(exclude_none=True)
    deps = cliente.ClienteDependencies(
        lista_precio_gateway=gateway_provider.lista_precio_gateway
    )
    item = handlers.update_cliente(
        gateway_provider.cliente_gateway, cliente_id, deps, data
    )
    if item is None:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return item


@router.delete(f"{CLIENTE_BASE}/{{cliente_id}}")
@router.delete(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_delete(cliente_id: int) -> Dict[str, Any]:
    ensure_write_allowed()
    ok = handlers.delete_cliente(gateway_provider.cliente_gateway, cliente_id)
    if not ok:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return {"status": "deleted", "cliente_id": cliente_id}
