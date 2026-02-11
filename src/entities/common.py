from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class SimpleItem:
    ID: Optional[int] = None
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    productoid: Optional[int] = None
    id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["SimpleItem"]:
        if not data:
            return None
        return cls(
            ID=data.get("ID"),
            nombre=data.get("nombre"),
            codigo=data.get("codigo"),
            productoid=data.get("productoid") or data.get("productoId"),
            id=data.get("id"),
        )


def drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: drop_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [drop_none(v) for v in value]
    return value
