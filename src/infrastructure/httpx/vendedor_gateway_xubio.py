"""
Path: src/infrastructure/httpx/vendedor_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

from ...shared.id_mapping import match_any_id
from ...shared.logger import get_logger
from ...use_cases.ports.vendedor_gateway import VendedorGateway
from .xubio_cache_helpers import (
    cache_get,
    cache_set,
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_crud_helpers import list_items

logger = get_logger(__name__)

VENDEDOR_PATH = "/API/1.1/vendedorBean"
VENDEDOR_ID_KEYS = ("vendedorId", "ID", "id")
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class XubioVendedorGateway(VendedorGateway):
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
            list_cache_ttl = read_cache_ttl("XUBIO_VENDEDOR_LIST_TTL")
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
        url = self._url(VENDEDOR_PATH)
        items = list_items(
            url=url, timeout=self._timeout, label="vendedores", logger=logger
        )
        self._store_cache(items)
        return items

    def get(self, vendedor_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if match_any_id(item, vendedor_id, VENDEDOR_ID_KEYS):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached = cache_get(_GLOBAL_LIST_CACHE, VENDEDOR_PATH, ttl=self._list_cache_ttl)
        if cached is not None:
            logger.info("Xubio lista vendedores: cache hit (%d items)", len(cached))
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        cache_set(_GLOBAL_LIST_CACHE, VENDEDOR_PATH, items, ttl=self._list_cache_ttl)

