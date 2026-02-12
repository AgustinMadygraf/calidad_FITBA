from fastapi import Request
from fastapi.responses import JSONResponse

from ...shared.config import is_prod

_MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


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
