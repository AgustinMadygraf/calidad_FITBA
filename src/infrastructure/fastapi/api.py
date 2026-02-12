"""
Path: src/infrastructure/fastapi/api.py
"""

from pathlib import Path
from typing import Any, Dict

import uvicorn
from fastapi import HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ...interface_adapter.controllers import handlers
from ...interface_adapter.schemas.cliente import ClientePayload
from ...interface_adapter.schemas.remito_venta import RemitoVentaPayload
from ...shared.config import get_host, get_port, is_prod, load_env
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from ...use_cases import cliente, remito_venta
from .deps import (
    get_categoria_fiscal_gateway,
    get_cliente_gateway,
    get_deposito_gateway,
    get_identificacion_tributaria_gateway,
    get_lista_precio_gateway,
    get_moneda_gateway,
    get_producto_compra_gateway,
    get_producto_gateway,
    get_remito_gateway,
    get_token_gateway,
)
from .app import app

logger = get_logger(__name__)


load_env()
token_gateway = get_token_gateway()
FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


def _get_cliente_gateway():
    if not hasattr(app, "cliente_gateway"):
        app.cliente_gateway = get_cliente_gateway()
    return app.cliente_gateway


def _get_categoria_fiscal_gateway():
    if not hasattr(app, "categoria_fiscal_gateway"):
        app.categoria_fiscal_gateway = get_categoria_fiscal_gateway()
    return app.categoria_fiscal_gateway


def _get_remito_gateway():
    if not hasattr(app, "remito_gateway"):
        app.remito_gateway = get_remito_gateway()
    return app.remito_gateway


def _get_producto_gateway():
    if not hasattr(app, "producto_gateway"):
        app.producto_gateway = get_producto_gateway()
    return app.producto_gateway


def _get_producto_compra_gateway():
    if not hasattr(app, "producto_compra_gateway"):
        app.producto_compra_gateway = get_producto_compra_gateway()
    return app.producto_compra_gateway


def _get_deposito_gateway():
    if not hasattr(app, "deposito_gateway"):
        app.deposito_gateway = get_deposito_gateway()
    return app.deposito_gateway


def _get_identificacion_tributaria_gateway():
    if not hasattr(app, "identificacion_tributaria_gateway"):
        app.identificacion_tributaria_gateway = get_identificacion_tributaria_gateway()
    return app.identificacion_tributaria_gateway


def _get_lista_precio_gateway():
    if not hasattr(app, "lista_precio_gateway"):
        app.lista_precio_gateway = get_lista_precio_gateway()
    return app.lista_precio_gateway


def _get_moneda_gateway():
    if not hasattr(app, "moneda_gateway"):
        app.moneda_gateway = get_moneda_gateway()
    return app.moneda_gateway


def _build_remito_dependencies() -> remito_venta.RemitoDependencies:
    return remito_venta.RemitoDependencies(
        cliente_gateway=_get_cliente_gateway(),
        producto_gateway=_get_producto_gateway(),
        deposito_gateway=_get_deposito_gateway(),
        lista_precio_gateway=_get_lista_precio_gateway(),
    )


def _resolve_remito_transaccion_id(
    data: Dict[str, Any],
    *,
    path_transaccion_id: int | None = None,
) -> int:
    raw_body_id = data.get("transaccionId")
    if raw_body_id is None:
        if path_transaccion_id is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "transaccionId es requerido en body para "
                    "PUT /API/1.1/remitoVentaBean"
                ),
            )
        data["transaccionId"] = path_transaccion_id
        return path_transaccion_id

    try:
        body_transaccion_id = int(raw_body_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400, detail="transaccionId debe ser un entero positivo"
        ) from exc

    if body_transaccion_id <= 0:
        raise HTTPException(
            status_code=400, detail="transaccionId debe ser un entero positivo"
        )

    if (
        path_transaccion_id is not None
        and body_transaccion_id != path_transaccion_id
    ):
        raise HTTPException(
            status_code=400,
            detail="transaccionId en body debe coincidir con el path",
        )

    data["transaccionId"] = body_transaccion_id
    return body_transaccion_id


CLIENTE_BASE = "/API/1.1/clienteBean"
CLIENTE_BASE_SLASH = "/API/1.1/clienteBean/"
CATEGORIA_FISCAL_BASE = "/API/1.1/categoriaFiscal"
CATEGORIA_FISCAL_BASE_SLASH = "/API/1.1/categoriaFiscal/"
PRODUCTO_BASE = "/API/1.1/ProductoVentaBean"
PRODUCTO_BASE_SLASH = "/API/1.1/ProductoVentaBean/"
PRODUCTO_COMPRA_BASE = "/API/1.1/ProductoCompraBean"
PRODUCTO_COMPRA_BASE_SLASH = "/API/1.1/ProductoCompraBean/"
LEGACY_PRODUCTO_BASE = "/API/1.1/productoVentaBean"
LEGACY_PRODUCTO_BASE_SLASH = "/API/1.1/productoVentaBean/"
LEGACY_PRODUCTO_COMPRA_BASE = "/API/1.1/productoCompraBean"
LEGACY_PRODUCTO_COMPRA_BASE_SLASH = "/API/1.1/productoCompraBean/"
DEPOSITO_BASE = "/API/1.1/depositos"
DEPOSITO_BASE_SLASH = "/API/1.1/depositos/"
IDENTIFICACION_TRIBUTARIA_BASE = "/API/1.1/identificacionTributaria"
IDENTIFICACION_TRIBUTARIA_BASE_SLASH = "/API/1.1/identificacionTributaria/"
LISTA_PRECIO_BASE = "/API/1.1/listaPrecioBean"
LISTA_PRECIO_BASE_SLASH = "/API/1.1/listaPrecioBean/"
MONEDA_BASE = "/API/1.1/monedaBean"
MONEDA_BASE_SLASH = "/API/1.1/monedaBean/"
_MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


@app.get("/", include_in_schema=False)
def root():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return handlers.root()


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health")
def health() -> Dict[str, str]:
    return handlers.health()


@app.middleware("http")
async def block_mutations_when_read_only(request: Request, call_next):
    if (
        request.method in _MUTATION_METHODS
        and request.url.path.startswith("/API/1.1/")
        and not is_prod()
    ):
        return JSONResponse(
            status_code=403,
            content={"detail": "Modo solo lectura: IS_PROD debe ser true"},
        )
    return await call_next(request)


def _ensure_write_allowed() -> None:
    if not is_prod():
        raise HTTPException(
            status_code=403, detail="Modo solo lectura: IS_PROD debe ser true"
        )


def _ensure_debug_allowed() -> None:
    if is_prod():
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/token/inspect")
def token_inspect() -> Dict[str, Any]:
    try:
        return handlers.inspect_token(token_gateway)
    except ValueError as exc:
        logger.error("Token inspect error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Token inspect error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get(CLIENTE_BASE)
@app.get(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_list() -> Dict[str, Any]:
    try:
        gateway = _get_cliente_gateway()
        return handlers.list_clientes(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar clientes: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(CATEGORIA_FISCAL_BASE)
@app.get(CATEGORIA_FISCAL_BASE_SLASH, include_in_schema=False)
def categoria_fiscal_list() -> Dict[str, Any]:
    try:
        gateway = _get_categoria_fiscal_gateway()
        return handlers.list_categorias_fiscales(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar categorias fiscales: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{CATEGORIA_FISCAL_BASE}/{{categoria_fiscal_id}}")
@app.get(f"{CATEGORIA_FISCAL_BASE}/{{categoria_fiscal_id}}/", include_in_schema=False)
def categoria_fiscal_get(categoria_fiscal_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_categoria_fiscal_gateway()
        item = handlers.get_categoria_fiscal(gateway, categoria_fiscal_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener categoria fiscal: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="categoria fiscal no encontrada")
    return item


@app.get("/debug/clienteBean")
def cliente_list_debug() -> Dict[str, Any]:
    _ensure_debug_allowed()
    try:
        gateway = _get_cliente_gateway()
        return handlers.debug_clientes(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error en debug cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(CLIENTE_BASE)
@app.post(CLIENTE_BASE_SLASH, include_in_schema=False)
def cliente_create(body: ClientePayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        gateway = _get_cliente_gateway()
        deps = cliente.ClienteDependencies(
            lista_precio_gateway=_get_lista_precio_gateway()
        )
        return handlers.create_cliente(gateway, deps, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        logger.error("Gateway error al crear cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{CLIENTE_BASE}/{{cliente_id}}")
@app.get(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_get(cliente_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_cliente_gateway()
        item = handlers.get_cliente(gateway, cliente_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="cliente no encontrado")
    return item


@app.put(f"{CLIENTE_BASE}/{{cliente_id}}")
@app.put(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
@app.patch(f"{CLIENTE_BASE}/{{cliente_id}}")
@app.patch(f"{CLIENTE_BASE}/{{cliente_id}}/", include_in_schema=False)
def cliente_update(cliente_id: int, body: ClientePayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        gateway = _get_cliente_gateway()
        deps = cliente.ClienteDependencies(
            lista_precio_gateway=_get_lista_precio_gateway()
        )
        item = handlers.update_cliente(gateway, cliente_id, deps, data)
    except ExternalServiceError as exc:
        logger.error("Gateway error al actualizar cliente: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
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
        raise HTTPException(status_code=502, detail=str(exc)) from exc
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
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(REMITO_BASE)
@app.post(REMITO_BASE_SLASH, include_in_schema=False)
def remito_create(body: RemitoVentaPayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        gateway = _get_remito_gateway()
        deps = _build_remito_dependencies()
        return handlers.create_remito(gateway, deps, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        logger.error("Gateway error al crear remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.put(REMITO_BASE)
@app.put(REMITO_BASE_SLASH, include_in_schema=False)
def remito_update_by_body(body: RemitoVentaPayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        transaccion_id = _resolve_remito_transaccion_id(data)
        gateway = _get_remito_gateway()
        deps = _build_remito_dependencies()
        item = handlers.update_remito(gateway, transaccion_id, deps, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        logger.error("Gateway error al actualizar remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return item


@app.get(f"{REMITO_BASE}/{{transaccion_id}}")
@app.get(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_get(transaccion_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_remito_gateway()
        item = handlers.get_remito(gateway, transaccion_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return item


@app.put(f"{REMITO_BASE}/{{transaccion_id}}")
@app.put(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
@app.patch(f"{REMITO_BASE}/{{transaccion_id}}")
@app.patch(f"{REMITO_BASE}/{{transaccion_id}}/", include_in_schema=False)
def remito_update(transaccion_id: int, body: RemitoVentaPayload) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        data = body.model_dump(exclude_none=True)
        transaccion_id = _resolve_remito_transaccion_id(
            data, path_transaccion_id=transaccion_id
        )
        gateway = _get_remito_gateway()
        deps = _build_remito_dependencies()
        item = handlers.update_remito(gateway, transaccion_id, deps, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExternalServiceError as exc:
        logger.error("Gateway error al actualizar remito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
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
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=404, detail="remito no encontrado")
    return {"status": "deleted", "transaccionId": transaccion_id}


@app.get(PRODUCTO_BASE)
@app.get(PRODUCTO_BASE_SLASH, include_in_schema=False)
@app.get(LEGACY_PRODUCTO_BASE, include_in_schema=False)
@app.get(LEGACY_PRODUCTO_BASE_SLASH, include_in_schema=False)
def producto_list() -> Dict[str, Any]:
    try:
        gateway = _get_producto_gateway()
        return handlers.list_productos(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar productos: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{PRODUCTO_BASE}/{{producto_id}}")
@app.get(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@app.get(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@app.get(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
def producto_get(producto_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_producto_gateway()
        item = handlers.get_producto(gateway, producto_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener producto: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return item


@app.post(PRODUCTO_BASE)
@app.post(PRODUCTO_BASE_SLASH, include_in_schema=False)
@app.post(LEGACY_PRODUCTO_BASE, include_in_schema=False)
@app.post(LEGACY_PRODUCTO_BASE_SLASH, include_in_schema=False)
def producto_create(body: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_producto_gateway()
        return handlers.create_producto(gateway, body)
    except ExternalServiceError as exc:
        logger.error("Gateway error al crear producto: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.put(f"{PRODUCTO_BASE}/{{producto_id}}")
@app.put(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@app.patch(f"{PRODUCTO_BASE}/{{producto_id}}")
@app.patch(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@app.put(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@app.put(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@app.patch(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@app.patch(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
def producto_update(producto_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_producto_gateway()
        item = handlers.update_producto(gateway, producto_id, body)
    except ExternalServiceError as exc:
        logger.error("Gateway error al actualizar producto: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return item


@app.delete(f"{PRODUCTO_BASE}/{{producto_id}}")
@app.delete(f"{PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
@app.delete(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}", include_in_schema=False)
@app.delete(f"{LEGACY_PRODUCTO_BASE}/{{producto_id}}/", include_in_schema=False)
def producto_delete(producto_id: int) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_producto_gateway()
        ok = handlers.delete_producto(gateway, producto_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al borrar producto: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return {"status": "deleted", "productoid": producto_id}


@app.get(PRODUCTO_COMPRA_BASE)
@app.get(PRODUCTO_COMPRA_BASE_SLASH, include_in_schema=False)
@app.get(LEGACY_PRODUCTO_COMPRA_BASE, include_in_schema=False)
@app.get(LEGACY_PRODUCTO_COMPRA_BASE_SLASH, include_in_schema=False)
def producto_compra_list() -> Dict[str, Any]:
    try:
        gateway = _get_producto_compra_gateway()
        return handlers.list_productos(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar productos compra: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{PRODUCTO_COMPRA_BASE}/{{producto_id}}")
@app.get(f"{PRODUCTO_COMPRA_BASE}/{{producto_id}}/", include_in_schema=False)
@app.get(f"{LEGACY_PRODUCTO_COMPRA_BASE}/{{producto_id}}", include_in_schema=False)
@app.get(f"{LEGACY_PRODUCTO_COMPRA_BASE}/{{producto_id}}/", include_in_schema=False)
def producto_compra_get(producto_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_producto_compra_gateway()
        item = handlers.get_producto(gateway, producto_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener producto compra: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return item


@app.get(DEPOSITO_BASE)
@app.get(DEPOSITO_BASE_SLASH, include_in_schema=False)
def deposito_list() -> Dict[str, Any]:
    try:
        gateway = _get_deposito_gateway()
        return handlers.list_depositos(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar depositos: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{DEPOSITO_BASE}/{{deposito_id}}")
@app.get(f"{DEPOSITO_BASE}/{{deposito_id}}/", include_in_schema=False)
def deposito_get(deposito_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_deposito_gateway()
        item = handlers.get_deposito(gateway, deposito_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener deposito: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="deposito no encontrado")
    return item


@app.get(IDENTIFICACION_TRIBUTARIA_BASE)
@app.get(IDENTIFICACION_TRIBUTARIA_BASE_SLASH, include_in_schema=False)
def identificacion_tributaria_list() -> Dict[str, Any]:
    try:
        gateway = _get_identificacion_tributaria_gateway()
        return handlers.list_identificaciones_tributarias(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar identificaciones tributarias: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{IDENTIFICACION_TRIBUTARIA_BASE}/{{identificacion_tributaria_id}}")
@app.get(
    f"{IDENTIFICACION_TRIBUTARIA_BASE}/{{identificacion_tributaria_id}}/",
    include_in_schema=False,
)
def identificacion_tributaria_get(identificacion_tributaria_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_identificacion_tributaria_gateway()
        item = handlers.get_identificacion_tributaria(
            gateway, identificacion_tributaria_id
        )
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener identificacion tributaria: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(
            status_code=404, detail="identificacion tributaria no encontrada"
        )
    return item


@app.get(LISTA_PRECIO_BASE)
@app.get(LISTA_PRECIO_BASE_SLASH, include_in_schema=False)
def lista_precio_list() -> Dict[str, Any]:
    try:
        gateway = _get_lista_precio_gateway()
        return handlers.list_lista_precios(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar listas de precio: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@app.get(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_get(lista_precio_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_lista_precio_gateway()
        item = handlers.get_lista_precio(gateway, lista_precio_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener lista de precio: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return item


@app.post(LISTA_PRECIO_BASE)
@app.post(LISTA_PRECIO_BASE_SLASH, include_in_schema=False)
def lista_precio_create(body: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_lista_precio_gateway()
        return handlers.create_lista_precio(gateway, body)
    except ExternalServiceError as exc:
        logger.error("Gateway error al crear lista de precio: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.put(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@app.put(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_update(lista_precio_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_lista_precio_gateway()
        item = handlers.update_lista_precio(gateway, lista_precio_id, body)
    except ExternalServiceError as exc:
        logger.error("Gateway error al actualizar lista de precio: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return item


@app.patch(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@app.patch(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_patch(lista_precio_id: int, body: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_lista_precio_gateway()
        item = handlers.patch_lista_precio(gateway, lista_precio_id, body)
    except ExternalServiceError as exc:
        logger.error("Gateway error al modificar lista de precio: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return item


@app.delete(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}")
@app.delete(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_delete(lista_precio_id: int) -> Dict[str, Any]:
    _ensure_write_allowed()
    try:
        gateway = _get_lista_precio_gateway()
        ok = handlers.delete_lista_precio(gateway, lista_precio_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al borrar lista de precio: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    return {"status": "deleted", "listaPrecioID": lista_precio_id}


@app.get(MONEDA_BASE)
@app.get(MONEDA_BASE_SLASH, include_in_schema=False)
def moneda_list() -> Dict[str, Any]:
    try:
        gateway = _get_moneda_gateway()
        return handlers.list_monedas(gateway)
    except ExternalServiceError as exc:
        logger.error("Gateway error al listar monedas: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get(f"{MONEDA_BASE}/{{moneda_id}}")
@app.get(f"{MONEDA_BASE}/{{moneda_id}}/", include_in_schema=False)
def moneda_get(moneda_id: int) -> Dict[str, Any]:
    try:
        gateway = _get_moneda_gateway()
        item = handlers.get_moneda(gateway, moneda_id)
    except ExternalServiceError as exc:
        logger.error("Gateway error al obtener moneda: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="moneda no encontrada")
    return item


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    logger.warning("Directorio frontend no encontrado: %s", FRONTEND_DIR)


def run() -> None:
    host = get_host()
    port = get_port()
    logger.info("Iniciando FastAPI en %s:%d", host, port)
    uvicorn.run(
        "src.infrastructure.fastapi.api:app", host=host, port=port, reload=True
    )


if __name__ == "__main__":
    run()
