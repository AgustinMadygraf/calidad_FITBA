"""
Path: src/infrastructure/httpx/cliente_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

import time

from ...use_cases.ports.cliente_gateway import ClienteGateway
from ...shared.logger import get_logger
from .xubio_cache_helpers import read_cache_ttl
from .xubio_crud_helpers import (
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)

logger = get_logger(__name__)

CLIENTE_PATH = "/API/1.1/clienteBean"
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class XubioClienteGateway(ClienteGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_CLIENTE_LIST_TTL", default=30.0)
        self._list_cache_ttl = list_cache_ttl

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            return cached
        url = self._url(CLIENTE_PATH)
        items = list_items(
            url=url, timeout=self._timeout, label="clientes", logger=logger
        )
        self._store_cache(items)
        return items

    def get(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            for item in cached:
                if _match_cliente_id(item, cliente_id):
                    return item
        url = self._url(f"{CLIENTE_PATH}/{cliente_id}")
        return get_item(url=url, timeout=self._timeout, logger=logger)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(CLIENTE_PATH)
        created = create_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache()
        return created

    def update(self, cliente_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = self._url(f"{CLIENTE_PATH}/{cliente_id}")
        updated = update_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache()
        return updated

    def delete(self, cliente_id: int) -> bool:
        url = self._url(f"{CLIENTE_PATH}/{cliente_id}")
        deleted = delete_item(url=url, timeout=self._timeout, logger=logger)
        if deleted:
            self._clear_list_cache()
        return deleted

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached: Optional[List[Dict[str, Any]]] = None
        if self._list_cache_ttl > 0:
            entry = _GLOBAL_LIST_CACHE.get(CLIENTE_PATH)
            if entry is not None:
                timestamp, items = entry
                if time.time() - timestamp <= self._list_cache_ttl:
                    logger.info(
                        "Xubio lista clientes: cache hit (%d items)", len(items)
                    )
                    cached = list(items)
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        if self._list_cache_ttl <= 0:
            return
        _GLOBAL_LIST_CACHE[CLIENTE_PATH] = (time.time(), list(items))

    def _clear_list_cache(self) -> None:
        _GLOBAL_LIST_CACHE.pop(CLIENTE_PATH, None)


def _match_cliente_id(item: Dict[str, Any], cliente_id: int) -> bool:
    for key in ("cliente_id", "clienteId", "ID", "id"):
        value = item.get(key)
        if value == cliente_id:
            return True
    return False
