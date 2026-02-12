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
from ...shared.config import get_host, get_port, load_env
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .app import app
from .deps import get_token_gateway
from .middleware import block_mutations_when_read_only
from .remito_utils import resolve_remito_transaccion_id
from .routers import (
    catalogos,
    cliente as cliente_router,
    comprobante_venta as comprobante_router,
    lista_precio as lista_precio_router,
    producto as producto_router,
    remito as remito_router,
    vendedor as vendedor_router,
)

logger = get_logger(__name__)

load_env()
token_gateway = get_token_gateway()
FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


# Kept for tests

def _resolve_remito_transaccion_id(
    data: Dict[str, Any],
    *,
    path_transaccion_id: int | None = None,
) -> int:
    return resolve_remito_transaccion_id(
        data, path_transaccion_id=path_transaccion_id
    )


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


app.middleware("http")(block_mutations_when_read_only)


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


@app.exception_handler(ExternalServiceError)
def external_service_error_handler(
    request: Request, exc: ExternalServiceError
) -> JSONResponse:
    logger.error("Gateway error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.warning("Value error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(cliente_router.router)
app.include_router(remito_router.router)
app.include_router(producto_router.router)
app.include_router(lista_precio_router.router)
app.include_router(vendedor_router.router)
app.include_router(comprobante_router.router)
app.include_router(catalogos.router)


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
