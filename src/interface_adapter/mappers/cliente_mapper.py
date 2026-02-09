from typing import Any, Dict

from ...entities.cliente import Cliente


def to_entity(payload: Dict[str, Any]) -> Cliente:
    return Cliente.from_dict(payload)


def to_dict(entity: Cliente, *, exclude_none: bool = False) -> Dict[str, Any]:
    return entity.to_dict(exclude_none=exclude_none)
