"""
Path: src/infrastructure/memory/producto_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...use_cases.ports.producto_gateway import ProductoGateway


class InMemoryProductoGateway(ProductoGateway):
    def __init__(self) -> None:
        self._items: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def list(self) -> List[Dict[str, Any]]:
        return [self._items[k] for k in sorted(self._items.keys())]

    def get(self, producto_id: int) -> Optional[Dict[str, Any]]:
        return self._items.get(producto_id)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        producto_id = self._next_id
        self._next_id += 1

        record = dict(data)
        record["productoid"] = producto_id
        self._items[producto_id] = record
        return record
