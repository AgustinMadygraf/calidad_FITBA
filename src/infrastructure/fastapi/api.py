"""
Path: src/infrastructure/fastapi/api.py
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException

from ...interface_adapter.controllers import handlers
from ...interface_adapter.schemas.cliente import ClientePayload
from ...interface_adapter.schemas.remito_venta import RemitoVentaPayload
from ...shared.config import is_prod, load_env
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .deps import get_cliente_gateway, get_remito_gateway, get_token_gateway
from .app import app

logger = get_logger(__name__)


load_env()
token_gateway = get_token_gateway()


def _get_cliente_gateway():
    if not hasattr(app, "cliente_gateway"):
        app.cliente_gateway = get_cliente_gateway()
    return app.cliente_gateway


def _get_remito_gateway():
    if not hasattr(app, "remito_gateway"):
        app.remito_gateway = get_remito_gateway()
    return app.remito_gateway
CLIENTE_BASE = "/API/1.1/clienteBean"
CLIENTE_BASE_SLASH = "/API/1.1/clienteBean/"


@app.get("/")
def root() -> Dict[str, str]:
    return handlers.root()


@app.get("/health")
def health() -> Dict[str, str]:
    return handlers.health()


def _ensure_write_allowed() -> None:
    if not is_prod():
        raise HTTPException(status_code=403, detail="Modo solo lectura: IS_PROD debe ser true")


def _ensure_debug_allowed() -> None:
    if is_prod():
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/token/inspect")
def token_inspect() -> Dict[str, Any]:
    try:
        return handlers.inspect_token(token_gateway)
    except ValueError as exc:
        logger.error("Token inspect error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Token inspect error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get(CLIENTE_BASE)
@app.get(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_list() -> Dict[str, Any]:
    try:
        gateway = _get_cliente_gateway()
        return handlers.list_clientes(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar clientes: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/debug/clienteBean")
def cliente_list_debug() -> Dict[str, Any]:
    _ensure_debug_allowed()
    try:
        gateway = _get_cliente_gateway()
        return handlers.debug_clientes(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error en debug cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.post(CLIENTE_BASE)
@app.post(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_create(body: ClientePayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        gateway = _get_cliente_gateway()
        return handlers.create_cliente(gateway, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ExternalServiceError as exc:
        logger.error("Gateway error al crear cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.get(f"{CLIENTE_BASE}/{{cliente_id}}")
@app.get(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_get(cliente_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_cliente_gateway()
        item = handlers.get_cliente(gateway, cliente_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if item is None:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return item


@app.put(f"{CLIENTE_BASE}/{{cliente_id}}")
@app.put(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_update(cliente_id: int, body: ClientePayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        gateway = _get_cliente_gateway()
        item = handlers.update_cliente(gateway, cliente_id, data)
    except ExternalServiceError as exc:
        logger.error("Gateway error al actualizar cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if item is None:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return item


@app.delete(f"{CLIENTE_BASE}/{{cliente_id}}")
@app.delete(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_delete(cliente_id: int) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_cliente_gateway()
        ok = handlers.delete_cliente(gateway, cliente_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al borrar cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return {"status": "deleted", "cliente_id": cliente_id}


REMITO_BASE = "/API/1.1/remitoVentaBean"
REMITO_BASE_SLASH = "/API/1.1/remitoVentaBean/"


@app.get(REMITO_BASE)
@app.get(REMITO_BASE_SLASH, include_in_schema=False)
def remito_list() -> Dict[str, Any]:
    try:
        gateway = _get_remito_gateway()
        return handlers.list_remitos(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar remitos: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.post(REMITO_BASE)
@app.post(REMITO_BASE_SLASH, include_in_schema=False)
def remito_create(body: RemitoVentaPayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        gateway = _get_remito_gateway()
        return handlers.create_remito(gateway, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ExternalServiceError as exc:
        logger.error("Gateway error al crear remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.get(f"{REMITO_BASE}/{{transaccion_id}}")
@app.get(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_get(transaccion_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_remito_gateway()
        item = handlers.get_remito(gateway, transaccion_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if item is None:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return item


@app.put(f"{REMITO_BASE}/{{transaccion_id}}")
@app.put(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_update(transaccion_id: int, body: RemitoVentaPayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        gateway = _get_remito_gateway()
        item = handlers.update_remito(gateway, transaccion_id, data)
    except ExternalServiceError as exc:
        logger.error("Gateway error al actualizar remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if item is None:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return item


@app.delete(f"{REMITO_BASE}/{{transaccion_id}}")
@app.delete(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_delete(transaccion_id: int) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_remito_gateway()
        ok = handlers.delete_remito(gateway, transaccion_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al borrar remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return {"status": "deleted", "transaccionId": transaccion_id}


def run() -> None:
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    logger.info("Iniciando FastAPI en 0.0.0.0:%d", port)
    uvicorn.run("src.infrastructure.fastapi.api:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run()
