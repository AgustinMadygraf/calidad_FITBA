from fastapi import Request
from fastapi.responses import JSONResponse

from ...shared.config import is_prod
from ...shared.logger import get_logger

logger = get_logger(__name__)

_MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


async def block_mutations_when_read_only(request: Request, call_next):
    # Log debug para requests en modo read-only
    if request.method in _MUTATION_METHODS and request.url.path.startswith("/API/1.1/"):
        if not is_prod():
            logger.warning(
                "Mutación bloqueada en modo read-only: %s %s (IS_PROD=false)",
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Modo solo lectura: IS_PROD debe ser true"},
            )
        else:
            logger.debug(
                "Mutación permitida en modo producción: %s %s",
                request.method,
                request.url.path,
            )
    return await call_next(request)
