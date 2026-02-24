from fastapi import HTTPException

def ensure_write_allowed() -> None:
    raise HTTPException(status_code=405, detail="Modo solo lectura: operacion no permitida")


def ensure_debug_allowed() -> None:
    raise HTTPException(status_code=404, detail="Not found")
