from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ....interface_adapter.schemas.remito_venta import RemitoVentaPayload
from ....shared.logger import get_logger
from ....use_cases import remito_venta
from ..gateway_provider import gateway_provider
from ..remito_utils import resolve_remito_transaccion_id
from ..runtime_policy import ensure_write_allowed

logger = get_logger(__name__)
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
    logger.info("▶️  GET /API/1.1/remitoVentaBean - inicio de consulta")
    try:
        result = handlers.list_remitos(gateway_provider.remito_gateway)
        logger.info("✅ GET /API/1.1/remitoVentaBean - completado, devolviendo %d items", len(result.get('items', [])))
        return result
    except Exception as e:
        logger.error("❌ GET /API/1.1/remitoVentaBean - error: %s", str(e)[:200], exc_info=True)
        raise


@router.post(REMITO_BASE)
@router.post(REMITO_BASE_SLASH, include_in_schema=False)
def remito_create(body: RemitoVentaPayload) -> Dict[str, Any]:
    logger.info("▶️  POST /API/1.1/remitoVentaBean - crear remito")
    try:
        ensure_write_allowed()
        data = body.model_dump(exclude_none=True)
        logger.debug("POST - datos recibidos (keys): %s", list(data.keys()))
        deps = _build_remito_dependencies()
        result = handlers.create_remito(gateway_provider.remito_gateway, deps, data)
        logger.info("✅ POST /API/1.1/remitoVentaBean - remito creado")
        return result
    except Exception as e:
        logger.error("❌ POST /API/1.1/remitoVentaBean - error: %s", str(e)[:200], exc_info=True)
        raise


@router.put(REMITO_BASE)
@router.put(REMITO_BASE_SLASH, include_in_schema=False)
def remito_update_by_body(body: RemitoVentaPayload) -> Dict[str, Any]:
    logger.info("▶️  PUT /API/1.1/remitoVentaBean - actualizar remito (por body)")
    try:
        ensure_write_allowed()
        data = body.model_dump(exclude_none=True)
        transaccion_id = resolve_remito_transaccion_id(data)
        logger.debug("PUT - actualizando remito %d", transaccion_id)
        deps = _build_remito_dependencies()
        item = handlers.update_remito(
            gateway_provider.remito_gateway, transaccion_id, deps, data
        )
        if item is None:
            logger.warning("⚠️  PUT remito %d - NO ENCONTRADO", transaccion_id)
            raise HTTPException(status_code=404, detail="remito no encontrado")
        logger.info("✅ PUT remito %d - actualizado", transaccion_id)
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ PUT /API/1.1/remitoVentaBean - error: %s", str(e)[:200], exc_info=True)
        raise


@router.get(f"{REMITO_BASE}/{{transaccion_id}}")
@router.get(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_get(transaccion_id: int) -> Dict[str, Any]:
    logger.debug("▶️  GET /API/1.1/remitoVentaBean/%d - obtener detalle", transaccion_id)
    try:
        item = handlers.get_remito(gateway_provider.remito_gateway, transaccion_id)
        if item is None:
            logger.warning("⚠️  GET remito %d - NO ENCONTRADO", transaccion_id)
            raise HTTPException(status_code=404, detail="remito no encontrado")
        logger.debug("✅ GET remito %d - encontrado", transaccion_id)
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ GET remito %d - error: %s", transaccion_id, str(e)[:200], exc_info=True)
        raise


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
    logger.info("▶️  DELETE /API/1.1/remitoVentaBean/%d - eliminar remito", transaccion_id)
    try:
        ensure_write_allowed()
        ok = handlers.delete_remito(gateway_provider.remito_gateway, transaccion_id)
        if not ok:
            logger.warning("⚠️  DELETE remito %d - NO ENCONTRADO", transaccion_id)
            raise HTTPException(status_code=404, detail="remito no encontrado")
        logger.info("✅ DELETE remito %d - eliminado", transaccion_id)
        return {"status": "deleted", "transaccionId": transaccion_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ DELETE remito %d - error: %s", transaccion_id, str(e)[:200], exc_info=True)
        raise
