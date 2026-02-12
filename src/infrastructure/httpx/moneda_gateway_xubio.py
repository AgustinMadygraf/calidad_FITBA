"""
Path: src/infrastructure/httpx/moneda_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

import time

from ...shared.logger import get_logger
from ...use_cases.ports.moneda_gateway import MonedaGateway
from .xubio_cache_helpers import read_cache_ttl
from .xubio_crud_helpers import list_items

logger = get_logger(__name__)

MONEDA_PATH = "/API/1.1/monedaBean"
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class XubioMonedaGateway(MonedaGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_MONEDA_LIST_TTL")
        self._list_cache_ttl = list_cache_ttl

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            return cached
        url = self._url(MONEDA_PATH)
        items = list_items(
            url=url, timeout=self._timeout, label="monedas", logger=logger
        )
        self._store_cache(items)
        return items

    def get(self, moneda_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_moneda_id(item, moneda_id):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached: Optional[List[Dict[str, Any]]] = None
        if self._list_cache_ttl > 0:
            entry = _GLOBAL_LIST_CACHE.get(MONEDA_PATH)
            if entry is not None:
                timestamp, items = entry
                if time.time() - timestamp <= self._list_cache_ttl:
                    logger.info("Xubio lista monedas: cache hit (%d items)", len(items))
                    cached = list(items)
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        if self._list_cache_ttl <= 0:
            return
        _GLOBAL_LIST_CACHE[MONEDA_PATH] = (time.time(), list(items))


def _match_moneda_id(item: Dict[str, Any], moneda_id: int) -> bool:
    for key in ("ID", "id"):
        value = item.get(key)
        if value == moneda_id:
            return True
    return False
