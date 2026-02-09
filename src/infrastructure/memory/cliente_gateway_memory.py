"""
Path: src/infrastructure/memory/cliente_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...interface_adapter.gateways.cliente_gateway import ClienteGateway

class InMemoryClienteGateway(ClienteGateway):
    def __init__(self) -> None:
        self._items: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def list(self) -> List[Dict[str, Any]]:
        return [self._items[k] for k in sorted(self._items.keys())]

    def list_raw(self) -> List[Dict[str, Any]]:
        return self.list()

    def get(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        return self._items.get(cliente_id)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        cliente_id = self._next_id
        self._next_id += 1

        record = dict(data)
        record["cliente_id"] = cliente_id
        self._items[cliente_id] = record
        return record

    def update(self, cliente_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if cliente_id not in self._items:
            return None
        record = dict(self._items[cliente_id])
        record.update(data)
        record["cliente_id"] = cliente_id
        self._items[cliente_id] = record
        return record

    def delete(self, cliente_id: int) -> bool:
        if cliente_id in self._items:
            del self._items[cliente_id]
            return True
        return False
