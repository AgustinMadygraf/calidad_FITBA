"""
Path: src/infrastructure/memory/lista_precio_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...use_cases.ports.lista_precio_gateway import ListaPrecioGateway


class InMemoryListaPrecioGateway(ListaPrecioGateway):
    def __init__(self) -> None:
        self._items: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def list(self) -> List[Dict[str, Any]]:
        return [self._items[k] for k in sorted(self._items.keys())]

    def get(self, lista_precio_id: int) -> Optional[Dict[str, Any]]:
        return self._items.get(lista_precio_id)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        lista_precio_id = self._next_id
        self._next_id += 1

        record = dict(data)
        record["listaPrecioID"] = lista_precio_id
        record["ID"] = lista_precio_id
        record["id"] = lista_precio_id
        self._items[lista_precio_id] = record
        return record

    def update(
        self, lista_precio_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if lista_precio_id not in self._items:
            return None
        record = dict(self._items[lista_precio_id])
        record.update(data)
        record["listaPrecioID"] = lista_precio_id
        record["ID"] = lista_precio_id
        record["id"] = lista_precio_id
        self._items[lista_precio_id] = record
        return record

    def patch(
        self, lista_precio_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return self.update(lista_precio_id, data)

    def delete(self, lista_precio_id: int) -> bool:
        if lista_precio_id in self._items:
            del self._items[lista_precio_id]
            return True
        return False
