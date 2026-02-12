"""
Path: src/infrastructure/httpx/deposito_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

from ...use_cases.ports.deposito_gateway import DepositoGateway
from ...shared.logger import get_logger
from .xubio_cache_helpers import (
    cache_get,
    cache_set,
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_crud_helpers import list_items

logger = get_logger(__name__)

DEPOSITO_PATH = "/API/1.1/depositos"
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class XubioDepositoGateway(DepositoGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
        enable_get_cache: Optional[bool] = None,
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_DEPOSITO_LIST_TTL")
        if enable_get_cache is None:
            enable_get_cache = default_get_cache_enabled()
        if not enable_get_cache:
            list_cache_ttl = 0.0
        self._list_cache_ttl = max(0.0, float(list_cache_ttl))

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            return cached
        url = self._url(DEPOSITO_PATH)
        items = list_items(
            url=url, timeout=self._timeout, label="depositos", logger=logger
        )
        self._store_cache(items)
        return items

    def get(self, deposito_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_deposito_id(item, deposito_id):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached = cache_get(_GLOBAL_LIST_CACHE, DEPOSITO_PATH, ttl=self._list_cache_ttl)
        if cached is not None:
            logger.info("Xubio lista depositos: cache hit (%d items)", len(cached))
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        cache_set(_GLOBAL_LIST_CACHE, DEPOSITO_PATH, items, ttl=self._list_cache_ttl)


def _match_deposito_id(item: Dict[str, Any], deposito_id: int) -> bool:
    for key in ("ID", "id", "depositoId"):
        value = item.get(key)
        if value == deposito_id:
            return True
    return False
