"""
Path: src/infrastructure/fastapi/api.py
"""

from typing import Any, Dict

import uvicorn
from fastapi import HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ...interface_adapter.controllers import handlers
from ...shared.config import (
    get_frontend_dev_proxy_url,
    get_frontend_cors_origins,
    get_host,
    get_port,
    get_static_dir,
    is_frontend_dev_proxy_enabled,
    is_frontend_dev_proxy_ws_enabled,
    load_env,
)
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .app import app
from .deps import get_token_gateway
from .middleware import block_mutations_when_read_only
from .frontend_proxy import build_frontend_proxy_middleware
from .frontend_proxy_ws import build_frontend_ws_proxy_handler
from .remito_utils import resolve_remito_transaccion_id
from .routers import (
    catalogos,
    cliente as cliente_router,
    comprobante_venta as comprobante_router,
    lista_precio as lista_precio_router,
    observability as observability_router,
    producto as producto_router,
    remito as remito_router,
    vendedor as vendedor_router,
)

logger = get_logger(__name__)

logger.debug("Inicializando FastAPI app...")
load_env()
logger.debug("Configuración de entorno cargada")
FRONTEND_CORS_ORIGINS = get_frontend_cors_origins()
FRONTEND_DEV_PROXY_ENABLED = is_frontend_dev_proxy_enabled()
FRONTEND_DEV_PROXY_URL = get_frontend_dev_proxy_url()
FRONTEND_DEV_PROXY_WS_ENABLED = is_frontend_dev_proxy_ws_enabled()

token_gateway = get_token_gateway()
logger.debug("Token gateway inicializado")

STATIC_DIR = get_static_dir()
FRONTEND_INDEX = STATIC_DIR / "index.html"

logger.info("Directorio estatico configurado: %s", STATIC_DIR)
logger.info(
    "Frontend dev proxy: enabled=%s url=%s",
    FRONTEND_DEV_PROXY_ENABLED,
    FRONTEND_DEV_PROXY_URL,
)
logger.info("Frontend dev proxy WS: enabled=%s", FRONTEND_DEV_PROXY_WS_ENABLED)
logger.debug("CORS origins configurados: %s", FRONTEND_CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],  # Permitir todos los headers (incluyendo ngrok-skip-browser-warning)
)
logger.debug("CORSMiddleware agregado con origins: %s", FRONTEND_CORS_ORIGINS)


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
        logger.debug("Sirviendo index del frontend: %s", FRONTEND_INDEX)
        return FileResponse(FRONTEND_INDEX)
    logger.warning(
        "No se encontro index del frontend en %s; devolviendo fallback API root",
        FRONTEND_INDEX,
    )
    return handlers.root()


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health")
def health() -> Dict[str, str]:
    logger.debug("GET /health invocado")
    return handlers.health()


@app.get("/API/health")
def api_health(request: Request) -> Dict[str, Any]:
    """Health check endpoint para validación rápida de API.
    
    Devuelve información de diagnóstico:
    - status: ok/error
    - origin: origen HTTP del request
    - content_type: application/json esperado
    
    Útil para detectar problemas de proxy/ngrok/caché.
    """
    origin = request.headers.get("origin", "no-origin-header")
    logger.debug("GET /API/health invocado desde origen: %s", origin)
    return {
        "status": "ok",
        "message": "API health check",
        "origin": origin,
        "referer": request.headers.get("referer", "no-referer"),
        "host": request.headers.get("host", request.url.netloc),
        "content_type": "application/json",
    }


app.middleware("http")(block_mutations_when_read_only)
if FRONTEND_DEV_PROXY_ENABLED:
    app.middleware("http")(build_frontend_proxy_middleware(FRONTEND_DEV_PROXY_URL))
if FRONTEND_DEV_PROXY_ENABLED and FRONTEND_DEV_PROXY_WS_ENABLED:
    app.add_api_websocket_route(
        "/{full_path:path}",
        build_frontend_ws_proxy_handler(FRONTEND_DEV_PROXY_URL),
        name="frontend_ws_proxy",
    )


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
    logger.error(
        "⚠️  Gateway error on %s %s (External service unavailable): %s",
        request.method,
        request.url.path,
        str(exc)[:200],
    )
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.warning(
        "⚠️  Value error on %s %s (Invalid request data): %s",
        request.method,
        request.url.path,
        str(exc)[:200],
    )
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(cliente_router.router)
app.include_router(remito_router.router)
app.include_router(producto_router.router)
app.include_router(lista_precio_router.router)
app.include_router(vendedor_router.router)
app.include_router(comprobante_router.router)
app.include_router(catalogos.router)
app.include_router(observability_router.router)


if STATIC_DIR.exists():
    logger.debug("StaticFiles directory encontrado: %s", STATIC_DIR)
    if not FRONTEND_INDEX.exists():
        logger.warning(
            "⚠️  Directorio estatico existe pero falta index.html: %s",
            FRONTEND_INDEX,
        )
    else:
        logger.debug("index.html encontrado en: %s", FRONTEND_INDEX)
    # NOTA: html=False para evitar que StaticFiles sirva index.html como fallback
    # a requests no coincidentes (ej: /API/1.1/*). Los routers tienen prioridad.
    logger.debug("Montando StaticFiles con html=False (sin fallback HTML)")
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=False), name="static")
else:
    logger.error("❌ CRÍTICO: Directorio estatico no encontrado: %s", STATIC_DIR)


def run() -> None:
    host = get_host()
    port = get_port()
    logger.info("Iniciando FastAPI en %s:%d", host, port)
    logger.debug("Uvicorn configured: host=%s, port=%d, reload=True", host, port)
    try:
        uvicorn.run(
            "src.infrastructure.fastapi.api:app", host=host, port=port, reload=True
        )
    except Exception as e:
        logger.error("❌ Error al iniciar servidor: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    run()
