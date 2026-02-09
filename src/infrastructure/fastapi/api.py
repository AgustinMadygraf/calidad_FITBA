"""
Path: src/infrastructure/fastapi/api.py
"""

from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from ...interface_adapter.controllers import handlers
from ...infrastructure.httpx.cliente_gateway_xubio import XubioClienteGateway
from ...infrastructure.httpx.token_gateway_httpx import HttpxTokenGateway
from ...infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from ...shared.config import is_prod, load_env
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .app import app

logger = get_logger(__name__)


class SimpleItem(BaseModel):
    ID: Optional[int] = None
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    id: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class Provincia(BaseModel):
    provincia_id: Optional[int] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    pais: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ClientePayload(BaseModel):
    cliente_id: Optional[int] = None
    nombre: Optional[str] = None
    primerApellido: Optional[str] = None
    segundoApellido: Optional[str] = None
    primerNombre: Optional[str] = None
    otrosNombres: Optional[str] = None
    razonSocial: Optional[str] = None
    nombreComercial: Optional[str] = None
    identificacionTributaria: Optional[SimpleItem] = None
    digitoVerificacion: Optional[str] = None
    categoriaFiscal: Optional[SimpleItem] = None
    provincia: Optional[Provincia] = None
    direccion: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    codigoPostal: Optional[str] = None
    cuentaVenta_id: Optional[SimpleItem] = None
    cuentaCompra_id: Optional[SimpleItem] = None
    pais: Optional[SimpleItem] = None
    localidad: Optional[SimpleItem] = None
    usrCode: Optional[str] = None
    listaPrecioVenta: Optional[SimpleItem] = None
    descripcion: Optional[str] = None
    esclienteextranjero: Optional[int] = None
    esProveedor: Optional[int] = None
    cuit: Optional[str] = None
    tipoDeOrganizacion: Optional[SimpleItem] = None
    responsabilidadOrganizacionItem: Optional[List[SimpleItem]] = None
    CUIT: Optional[str] = None

    model_config = ConfigDict(extra="allow")


load_env()
token_gateway = HttpxTokenGateway()
cliente_gateway = XubioClienteGateway() if is_prod() else InMemoryClienteGateway()
logger.info("Cliente gateway: %s", "XubioClienteGateway" if is_prod() else "InMemoryClienteGateway")
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
        return handlers.list_clientes(cliente_gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar clientes: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/debug/clienteBean")
def cliente_list_debug() -> Dict[str, Any]:
    try:
        resp = handlers.list_clientes_raw(cliente_gateway)
        # If in-memory, resp might be list; normalize for debug.
        if isinstance(resp, list):
            return {
                "status_code": 200,
                "content_type": "application/json",
                "body_preview": resp[:3],
            }
        return {
            "status_code": resp.status_code,
            "content_type": resp.headers.get("content-type"),
            "body_preview": resp.text[:500],
        }
    except ExternalServiceError as exc:
        logger.error("Gateway error en debug cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.post(CLIENTE_BASE)
@app.post(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_create(body: ClientePayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        return handlers.create_cliente(cliente_gateway, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ExternalServiceError as exc:
        logger.error("Gateway error al crear cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@app.get(f"{CLIENTE_BASE}/{{cliente_id}}")
@app.get(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_get(cliente_id: int) -> Dict[str, Any]:
    try:
        item = handlers.get_cliente(cliente_gateway, cliente_id)
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
        item = handlers.update_cliente(cliente_gateway, cliente_id, data)
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
        ok = handlers.delete_cliente(cliente_gateway, cliente_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al borrar cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return {"status": "deleted", "cliente_id": cliente_id}


def run() -> None:
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    logger.info("Iniciando FastAPI en 0.0.0.0:%d", port)
    uvicorn.run("src.infrastructure.fastapi.api:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run()
