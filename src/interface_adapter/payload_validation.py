from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class _ProductoPayloadModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    productoid: Optional[int] = None
    productoId: Optional[int] = None
    ID: Optional[int] = None
    id: Optional[int] = None
    nombre: Optional[str] = None
    codigo: Optional[str] = None


class _ListaPrecioPayloadModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    listaPrecioID: Optional[int] = None
    listaPrecioId: Optional[int] = None
    ID: Optional[int] = None
    id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


def validate_producto_payload(
    payload: Dict[str, Any], *, path_producto_id: Optional[int] = None
) -> Dict[str, Any]:
    parsed = _parse_producto_payload(payload)
    payload_id = _resolve_unique_positive_id(
        {
            "productoid": parsed.productoid,
            "productoId": parsed.productoId,
            "ID": parsed.ID,
            "id": parsed.id,
        },
        entity_label="producto",
    )
    if (
        path_producto_id is not None
        and payload_id is not None
        and payload_id != path_producto_id
    ):
        raise ValueError(
            "ID de producto en body debe coincidir con path "
            f"({payload_id} != {path_producto_id})"
        )
    return payload


def validate_lista_precio_payload(
    payload: Dict[str, Any], *, path_lista_precio_id: Optional[int] = None
) -> Dict[str, Any]:
    parsed = _parse_lista_precio_payload(payload)
    payload_id = _resolve_unique_positive_id(
        {
            "listaPrecioID": parsed.listaPrecioID,
            "listaPrecioId": parsed.listaPrecioId,
            "ID": parsed.ID,
            "id": parsed.id,
        },
        entity_label="lista de precio",
    )
    if (
        path_lista_precio_id is not None
        and payload_id is not None
        and payload_id != path_lista_precio_id
    ):
        raise ValueError(
            "ID de lista de precio en body debe coincidir con path "
            f"({payload_id} != {path_lista_precio_id})"
        )
    return payload


def _parse_producto_payload(payload: Dict[str, Any]) -> _ProductoPayloadModel:
    try:
        return _ProductoPayloadModel.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(_format_validation_error("producto", exc)) from exc


def _parse_lista_precio_payload(payload: Dict[str, Any]) -> _ListaPrecioPayloadModel:
    try:
        return _ListaPrecioPayloadModel.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(_format_validation_error("lista de precio", exc)) from exc


def _resolve_unique_positive_id(
    alias_values: Dict[str, Optional[int]], *, entity_label: str
) -> Optional[int]:
    present = [(alias, value) for alias, value in alias_values.items() if value is not None]
    if not present:
        return None

    unique_values = {value for _, value in present}
    if len(unique_values) > 1:
        aliases = ", ".join(f"{alias}={value}" for alias, value in present)
        raise ValueError(f"IDs inconsistentes para {entity_label}: {aliases}")

    resolved_id = present[0][1]
    if resolved_id is None:
        return None
    if resolved_id <= 0:
        raise ValueError(f"ID de {entity_label} debe ser > 0")
    return resolved_id


def _format_validation_error(entity_label: str, exc: ValidationError) -> str:
    first_error = exc.errors()[0]
    loc = first_error.get("loc") or ("body",)
    field_path = ".".join(str(part) for part in loc)
    message = first_error.get("msg", "valor invalido")
    return f"payload {entity_label} invalido en '{field_path}': {message}"
