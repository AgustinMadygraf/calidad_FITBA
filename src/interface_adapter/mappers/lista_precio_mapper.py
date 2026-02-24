from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ...shared.logger import get_logger

logger = get_logger(__name__)


def normalize_lista_precio_detail(
    payload: Dict[str, Any], *, resource_id: int
) -> Dict[str, Any]:
    data = dict(payload or {})
    patched_fields: List[str] = []

    lista_precio_id = _coalesce_int(
        data.get("listaPrecioID"),
        data.get("listaPrecioId"),
        data.get("ID"),
        data.get("id"),
        default=resource_id,
    )
    if "listaPrecioID" not in data:
        patched_fields.append("listaPrecioID")
    data["listaPrecioID"] = lista_precio_id

    data = _ensure_bool(data, "activo", default=True, patched_fields=patched_fields)
    data = _ensure_str(data, "nombre", default="", patched_fields=patched_fields)
    data = _ensure_str(data, "descripcion", default="", patched_fields=patched_fields)
    data = _ensure_bool(data, "esDefault", default=False, patched_fields=patched_fields)
    data = _ensure_int(data, "tipo", default=0, patched_fields=patched_fields)
    data = _ensure_int(data, "iva", default=0, patched_fields=patched_fields)
    data = _ensure_bool(
        data, "ocultarSinPrecio", default=False, patched_fields=patched_fields
    )

    data["moneda"], moneda_patched = _normalize_simple_item(
        data.get("moneda"), default_name="Pesos Argentinos"
    )
    patched_fields.extend(f"moneda.{name}" for name in moneda_patched)

    data["listaReferencia"], ref_patched = _normalize_simple_item(
        data.get("listaReferencia"), default_name=""
    )
    patched_fields.extend(f"listaReferencia.{name}" for name in ref_patched)

    normalized_items: List[Dict[str, Any]] = []
    raw_items = data.get("listaPrecioItem")
    if not isinstance(raw_items, list):
        raw_items = []
        patched_fields.append("listaPrecioItem")
    for idx, raw_item in enumerate(raw_items):
        item, item_patched = _normalize_lista_precio_item(
            raw_item, fallback_lista_precio_id=lista_precio_id
        )
        normalized_items.append(item)
        patched_fields.extend(f"listaPrecioItem[{idx}].{name}" for name in item_patched)
    data["listaPrecioItem"] = normalized_items

    if patched_fields:
        logger.warning(
            "ListaPrecio %s normalizada: faltaban/invalidos campos=%s",
            resource_id,
            ",".join(patched_fields),
        )
    return data


def _normalize_lista_precio_item(
    raw_item: Any, *, fallback_lista_precio_id: int
) -> Tuple[Dict[str, Any], List[str]]:
    item = dict(raw_item) if isinstance(raw_item, dict) else {}
    patched: List[str] = []

    if "listaPrecioID" not in item:
        patched.append("listaPrecioID")
    item["listaPrecioID"] = _coalesce_int(
        item.get("listaPrecioID"), default=fallback_lista_precio_id
    )

    item["producto"], producto_patched = _normalize_simple_item(
        item.get("producto"), default_name="Producto"
    )
    patched.extend(f"producto.{name}" for name in producto_patched)

    if "precio" not in item:
        patched.append("precio")
    item["precio"] = _coalesce_float(item.get("precio"), default=0.0)

    if "codigo" not in item:
        patched.append("codigo")
    item["codigo"] = str(item.get("codigo") or "")

    if "referencia" not in item:
        patched.append("referencia")
    item["referencia"] = _coalesce_float(item.get("referencia"), default=0.0)
    return item, patched


def _normalize_simple_item(
    raw: Any, *, default_name: str
) -> Tuple[Dict[str, Any], List[str]]:
    item = dict(raw) if isinstance(raw, dict) else {}
    patched: List[str] = []

    parsed_id = _coalesce_int(item.get("ID"), item.get("id"), default=0)
    if "ID" not in item:
        patched.append("ID")
    if "id" not in item:
        patched.append("id")
    item["ID"] = parsed_id
    item["id"] = parsed_id

    if "nombre" not in item:
        patched.append("nombre")
    item["nombre"] = str(item.get("nombre") or default_name)

    if "codigo" not in item:
        patched.append("codigo")
    item["codigo"] = str(item.get("codigo") or "")

    return item, patched


def _coalesce_int(*values: Any, default: int) -> int:
    for value in values:
        try:
            if value is None:
                continue
            return int(value)
        except (TypeError, ValueError):
            continue
    return default


def _coalesce_float(value: Any, *, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _ensure_bool(
    data: Dict[str, Any], key: str, *, default: bool, patched_fields: List[str]
) -> Dict[str, Any]:
    if key not in data:
        patched_fields.append(key)
    data[key] = bool(data.get(key, default))
    return data


def _ensure_str(
    data: Dict[str, Any], key: str, *, default: str, patched_fields: List[str]
) -> Dict[str, Any]:
    if key not in data:
        patched_fields.append(key)
    value = data.get(key, default)
    data[key] = default if value is None else str(value)
    return data


def _ensure_int(
    data: Dict[str, Any], key: str, *, default: int, patched_fields: List[str]
) -> Dict[str, Any]:
    if key not in data:
        patched_fields.append(key)
    data[key] = _coalesce_int(data.get(key), default=default)
    return data
