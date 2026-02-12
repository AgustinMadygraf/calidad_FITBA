from fastapi import HTTPException

from ...shared.config import is_prod


def ensure_write_allowed() -> None:
    if not is_prod():
        raise HTTPException(
            status_code=403, detail="Modo solo lectura: IS_PROD debe ser true"
        )


def ensure_debug_allowed() -> None:
    if is_prod():
        raise HTTPException(status_code=404, detail="Not found")
