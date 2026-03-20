from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ....shared.logger import get_logger
from ..gateway_provider import gateway_provider

logger = get_logger(__name__)
router = APIRouter()

REMITO_BASE = "/API/1.1/remitoVentaBean"
REMITO_BASE_SLASH = "/API/1.1/remitoVentaBean/"

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

