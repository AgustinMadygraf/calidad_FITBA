from typing import Any, Dict

from fastapi import HTTPException


def resolve_remito_transaccion_id(
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
