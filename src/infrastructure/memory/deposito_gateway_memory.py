"""
Path: src/infrastructure/memory/deposito_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...use_cases.ports.deposito_gateway import DepositoGateway


class InMemoryDepositoGateway(DepositoGateway):
    def __init__(self) -> None:
        self._items: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1

    def list(self) -> List[Dict[str, Any]]:
        return [self._items[k] for k in sorted(self._items.keys())]

    def get(self, deposito_id: int) -> Optional[Dict[str, Any]]:
        return self._items.get(deposito_id)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        deposito_id = self._next_id
        self._next_id += 1

        record = dict(data)
        record["id"] = deposito_id
        record["ID"] = deposito_id
        self._items[deposito_id] = record
        return record
