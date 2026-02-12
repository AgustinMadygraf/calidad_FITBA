"""
Path: src/infrastructure/httpx/lista_precio_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

import time

from ...shared.logger import get_logger
from ...use_cases.ports.lista_precio_gateway import ListaPrecioGateway
from .xubio_cache_helpers import read_cache_ttl
from .xubio_crud_helpers import list_items

logger = get_logger(__name__)

LISTA_PRECIO_PATH = "/API/1.1/listaPrecioBean"
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class XubioListaPrecioGateway(ListaPrecioGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_LISTA_PRECIO_LIST_TTL")
        self._list_cache_ttl = list_cache_ttl

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            return cached
        url = self._url(LISTA_PRECIO_PATH)
        items = list_items(
            url=url, timeout=self._timeout, label="listas_precio", logger=logger
        )
        self._store_cache(items)
        return items

    def get(self, lista_precio_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_lista_precio_id(item, lista_precio_id):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached: Optional[List[Dict[str, Any]]] = None
        if self._list_cache_ttl > 0:
            entry = _GLOBAL_LIST_CACHE.get(LISTA_PRECIO_PATH)
            if entry is not None:
                timestamp, items = entry
                if time.time() - timestamp <= self._list_cache_ttl:
                    logger.info(
                        "Xubio lista listas_precio: cache hit (%d items)",
                        len(items),
                    )
                    cached = list(items)
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        if self._list_cache_ttl <= 0:
            return
        _GLOBAL_LIST_CACHE[LISTA_PRECIO_PATH] = (time.time(), list(items))


def _match_lista_precio_id(item: Dict[str, Any], lista_precio_id: int) -> bool:
    for key in ("listaPrecioID", "listaPrecioId", "ID", "id"):
        value = item.get(key)
        if value == lista_precio_id:
            return True
    return False
