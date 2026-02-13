"""
Path: src/infrastructure/httpx/cliente_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

from ...use_cases.ports.cliente_gateway import ClienteGateway
from ...shared.id_mapping import extract_int_id, match_any_id
from ...shared.logger import get_logger
from .xubio_cache_helpers import (
    cache_get,
    cache_set,
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_crud_helpers import (
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)

logger = get_logger(__name__)

CLIENTE_PATH = "/API/1.1/clienteBean"
CLIENTE_ID_KEYS = ("cliente_id", "clienteId", "ID", "id")
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
_GLOBAL_ITEM_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


class XubioClienteGateway(ClienteGateway):
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
            list_cache_ttl = read_cache_ttl("XUBIO_CLIENTE_LIST_TTL", default=30.0)
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
        url = self._url(CLIENTE_PATH)
        items = list_items(
            url=url, timeout=self._timeout, label="clientes", logger=logger
        )
        self._store_cache(items)
        return items

    def get(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        cached_item = self._get_cached_item(cliente_id)
        if cached_item is not None:
            logger.info("Xubio cliente detalle: cache hit (%s)", cliente_id)
            return cached_item
        cached = self._get_cached_list()
        if cached is not None:
            for item in cached:
                if match_any_id(item, cliente_id, CLIENTE_ID_KEYS):
                    self._store_item_cache(cliente_id, item)
                    return item
        url = self._url(f"{CLIENTE_PATH}/{cliente_id}")
        item = get_item(url=url, timeout=self._timeout, logger=logger)
        if item is not None:
            self._store_item_cache(cliente_id, item)
        return item

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(CLIENTE_PATH)
        created = create_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache()
        self._clear_item_cache()
        return created

    def update(self, cliente_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = self._url(f"{CLIENTE_PATH}/{cliente_id}")
        updated = update_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache()
        self._clear_item_cache(cliente_id)
        return updated

    def delete(self, cliente_id: int) -> bool:
        url = self._url(f"{CLIENTE_PATH}/{cliente_id}")
        deleted = delete_item(url=url, timeout=self._timeout, logger=logger)
        if deleted:
            self._clear_list_cache()
            self._clear_item_cache(cliente_id)
        return deleted

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached = cache_get(_GLOBAL_LIST_CACHE, CLIENTE_PATH, ttl=self._list_cache_ttl)
        if cached is not None:
            logger.info("Xubio lista clientes: cache hit (%d items)", len(cached))
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        cache_set(_GLOBAL_LIST_CACHE, CLIENTE_PATH, items, ttl=self._list_cache_ttl)
        for item in items:
            item_id = extract_int_id(item, CLIENTE_ID_KEYS)
            if item_id is not None:
                self._store_item_cache(item_id, item)

    def _clear_list_cache(self) -> None:
        _GLOBAL_LIST_CACHE.pop(CLIENTE_PATH, None)

    def _get_cached_item(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        return cache_get(
            _GLOBAL_ITEM_CACHE,
            _cliente_item_cache_key(cliente_id),
            ttl=self._list_cache_ttl,
        )

    def _store_item_cache(self, cliente_id: int, item: Dict[str, Any]) -> None:
        cache_set(
            _GLOBAL_ITEM_CACHE,
            _cliente_item_cache_key(cliente_id),
            item,
            ttl=self._list_cache_ttl,
        )

    def _clear_item_cache(self, cliente_id: Optional[int] = None) -> None:
        if cliente_id is not None:
            _GLOBAL_ITEM_CACHE.pop(_cliente_item_cache_key(cliente_id), None)
            return
        _GLOBAL_ITEM_CACHE.clear()


def _cliente_item_cache_key(cliente_id: int) -> str:
    return f"{CLIENTE_PATH}/{cliente_id}"
