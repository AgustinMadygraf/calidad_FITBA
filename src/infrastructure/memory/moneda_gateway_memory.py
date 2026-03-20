"""
Path: src/infrastructure/memory/moneda_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...shared.id_mapping import match_any_id
from ...use_cases.ports.moneda_gateway import MonedaGateway


_DEFAULT_MONEDAS: List[Dict[str, Any]] = [
    {
        "ID": 0,
        "nombre": "Pesos Argentinos",
        "codigo": "string",
        "id": 0,
    }
]


class InMemoryMonedaGateway(MonedaGateway):
    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        source = items if items is not None else _DEFAULT_MONEDAS
        self._items = [dict(item) for item in source]

    def list(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self._items]

    def get(self, moneda_id: int) -> Optional[Dict[str, Any]]:
        for item in self._items:
            if match_any_id(item, moneda_id, ("ID", "id")):
                return dict(item)
        return None
