"""
Path: src/infrastructure/memory/vendedor_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...shared.id_mapping import match_any_id
from ...use_cases.ports.vendedor_gateway import VendedorGateway


_DEFAULT_VENDEDORES: List[Dict[str, Any]] = [
    {
        "vendedorId": 0,
        "nombre": "string",
        "apellido": "string",
        "esVendedor": 0,
        "activo": 0,
        "id": 0,
    }
]


class InMemoryVendedorGateway(VendedorGateway):
    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        source = items if items is not None else _DEFAULT_VENDEDORES
        self._items = [dict(item) for item in source]

    def list(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self._items]

    def get(self, vendedor_id: int) -> Optional[Dict[str, Any]]:
        for item in self._items:
            if match_any_id(item, vendedor_id, ("vendedorId", "ID", "id")):
                return dict(item)
        return None
