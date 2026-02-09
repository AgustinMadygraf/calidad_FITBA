from typing import Any, Dict, List, Optional

from ...use_cases.ports.remito_gateway import RemitoGateway


class InMemoryRemitoGateway(RemitoGateway):
    def __init__(self) -> None:
        self._items: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def list(self) -> List[Dict[str, Any]]:
        return [self._items[k] for k in sorted(self._items.keys())]

    def get(self, transaccion_id: int) -> Optional[Dict[str, Any]]:
        return self._items.get(transaccion_id)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        transaccion_id = self._next_id
        self._next_id += 1

        record = dict(data)
        record["transaccionId"] = transaccion_id
        self._items[transaccion_id] = record
        return record

    def update(self, transaccion_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if transaccion_id not in self._items:
            return None
        record = dict(self._items[transaccion_id])
        record.update(data)
        record["transaccionId"] = transaccion_id
        self._items[transaccion_id] = record
        return record

    def delete(self, transaccion_id: int) -> bool:
        if transaccion_id in self._items:
            del self._items[transaccion_id]
            return True
        return False
