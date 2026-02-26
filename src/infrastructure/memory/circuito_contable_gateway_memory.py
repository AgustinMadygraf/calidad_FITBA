"""
Path: src/infrastructure/memory/circuito_contable_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...shared.id_mapping import match_any_id
from ...use_cases.ports.circuito_contable_gateway import CircuitoContableGateway


_DEFAULT_CIRCUITOS_CONTABLES: List[Dict[str, Any]] = [
    {
        "circuitoContable_id": 0,
        "codigo": "string",
        "nombre": "string",
    }
]


class InMemoryCircuitoContableGateway(CircuitoContableGateway):
    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        source = items if items is not None else _DEFAULT_CIRCUITOS_CONTABLES
        self._items = [dict(item) for item in source]

    def list(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self._items]

    def get(self, circuito_contable_id: int) -> Optional[Dict[str, Any]]:
        for item in self._items:
            if match_any_id(item, circuito_contable_id, ("circuitoContable_id", "ID", "id")):
                return dict(item)
        return None
