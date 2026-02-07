from __future__ import annotations

from typing import Any

from src.entities.schemas import ProductOut


def extract_product_id(item: dict[str, Any]) -> str | None:
    value = item.get("productoid") or item.get("productoId") or item.get("id") or item.get("external_id")
    return str(value) if value is not None else None


def extract_product_name(item: dict[str, Any]) -> str:
    name = item.get("nombre") or item.get("name") or item.get("descripcion") or "SIN_NOMBRE"
    return " ".join(str(name).split())


def extract_product_price(item: dict[str, Any]) -> Any:
    return item.get("precioVenta") or item.get("precioUltCompra") or item.get("price") or "-"


def format_product_screen(item: dict[str, Any]) -> str:
    external_id = extract_product_id(item)
    name = extract_product_name(item)
    sku = item.get("codigo") or item.get("sku") or "-"
    price = extract_product_price(item)
    return "\n".join(
        [
            "Producto:",
            f"ID: {external_id}",
            f"Nombre: {name}",
            f"SKU: {sku}",
            f"Precio: {price}",
        ]
    )


def to_xubio(dto: ProductOut) -> dict[str, Any]:
    raw: dict[str, Any] = {}
    if getattr(dto, "xubio_payload", None):
        raw = dict(dto.xubio_payload or {})
    for key in ("name", "sku", "price", "external_id"):
        raw.pop(key, None)
    raw.setdefault("productoid", dto.external_id)
    raw.setdefault("nombre", dto.name)
    if dto.sku is not None:
        raw.setdefault("codigo", dto.sku)
    if dto.price is not None:
        raw.setdefault("precioVenta", dto.price)
    return raw
