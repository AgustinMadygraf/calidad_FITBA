"""
Path: src/infrastructure/memory/categoria_fiscal_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...shared.id_mapping import match_any_id
from ...use_cases.ports.categoria_fiscal_gateway import CategoriaFiscalGateway


_DEFAULT_CATEGORIAS_FISCALES: List[Dict[str, Any]] = [
    {"codigo": "CF", "nombre": "Consumidor Final", "id": 3, "ID": 3},
    {"codigo": "EX", "nombre": "Exento", "id": 5, "ID": 5},
    {"codigo": "CE", "nombre": "Exterior", "id": 6, "ID": 6},
    {"codigo": "NA", "nombre": "IVA No Alcanzado", "id": 7, "ID": 7},
    {"codigo": "MT", "nombre": "Monotributista", "id": 4, "ID": 4},
    {"codigo": "RI", "nombre": "Responsable Inscripto", "id": 1, "ID": 1},
]


class InMemoryCategoriaFiscalGateway(CategoriaFiscalGateway):
    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        source = items if items is not None else _DEFAULT_CATEGORIAS_FISCALES
        self._items = [dict(item) for item in source]

    def list(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self._items]

    def get(self, categoria_fiscal_id: int) -> Optional[Dict[str, Any]]:
        for item in self._items:
            if match_any_id(item, categoria_fiscal_id, ("ID", "id")):
                return dict(item)
        return None
