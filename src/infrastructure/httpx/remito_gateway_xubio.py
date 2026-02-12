from typing import Any, Dict, List, Optional, Tuple

import httpx

from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from ...use_cases.ports.remito_gateway import RemitoGateway
from .xubio_cache_helpers import (
    cache_get,
    cache_set,
    default_get_cache_enabled,
    read_cache_ttl,
)
from .token_client import request_with_token
from .xubio_crud_helpers import create_item, delete_item, list_items, update_item
from .xubio_httpx_helpers import raise_for_status

logger = get_logger(__name__)

REMITO_PATH = "/API/1.1/remitoVentaBean"
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
_GLOBAL_ITEM_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


class XubioRemitoGateway(RemitoGateway):
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
            list_cache_ttl = read_cache_ttl("XUBIO_REMITO_LIST_TTL", default=15.0)
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
        url = self._url(REMITO_PATH)
        items = list_items(
            url=url, timeout=self._timeout, label="remitos", logger=logger
        )
        self._store_cache(items)
        return items

    def get(self, transaccion_id: int) -> Optional[Dict[str, Any]]:
        cached_item = self._get_cached_item(transaccion_id)
        if cached_item is not None:
            logger.info("Xubio remito detalle: cache hit (%s)", transaccion_id)
            return cached_item
        cached = self._get_cached_list()
        if cached is not None:
            for item in cached:
                if item.get("transaccionId") == transaccion_id:
                    self._store_item_cache(transaccion_id, item)
                    return item
        url = self._url(f"{REMITO_PATH}/{transaccion_id}")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code == 404:
                return None
            if resp.status_code >= 500:
                logger.warning(
                    "Xubio GET %s failed with %s, falling back to list lookup",
                    url,
                    resp.status_code,
                )
                item = self._fallback_get_from_list(transaccion_id)
                if item is not None:
                    self._store_item_cache(transaccion_id, item)
                return item
            raise_for_status(resp)
            item = resp.json()
            self._store_item_cache(transaccion_id, item)
            return item
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(REMITO_PATH)
        created = create_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache()
        self._clear_item_cache()
        return created

    def update(
        self, transaccion_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        url = self._url(f"{REMITO_PATH}/{transaccion_id}")
        updated = update_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache()
        self._clear_item_cache(transaccion_id)
        return updated

    def delete(self, transaccion_id: int) -> bool:
        url = self._url(f"{REMITO_PATH}/{transaccion_id}")
        deleted = delete_item(url=url, timeout=self._timeout, logger=logger)
        if deleted:
            self._clear_list_cache()
            self._clear_item_cache(transaccion_id)
        return deleted

    def _fallback_get_from_list(self, transaccion_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if item.get("transaccionId") == transaccion_id:
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached = cache_get(_GLOBAL_LIST_CACHE, REMITO_PATH, ttl=self._list_cache_ttl)
        if cached is not None:
            logger.info("Xubio lista remitos: cache hit (%d items)", len(cached))
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        cache_set(_GLOBAL_LIST_CACHE, REMITO_PATH, items, ttl=self._list_cache_ttl)
        for item in items:
            transaccion_id = item.get("transaccionId")
            if isinstance(transaccion_id, int):
                self._store_item_cache(transaccion_id, item)

    def _clear_list_cache(self) -> None:
        _GLOBAL_LIST_CACHE.pop(REMITO_PATH, None)

    def _get_cached_item(self, transaccion_id: int) -> Optional[Dict[str, Any]]:
        return cache_get(
            _GLOBAL_ITEM_CACHE,
            _remito_item_cache_key(transaccion_id),
            ttl=self._list_cache_ttl,
        )

    def _store_item_cache(self, transaccion_id: int, item: Dict[str, Any]) -> None:
        cache_set(
            _GLOBAL_ITEM_CACHE,
            _remito_item_cache_key(transaccion_id),
            item,
            ttl=self._list_cache_ttl,
        )

    def _clear_item_cache(self, transaccion_id: Optional[int] = None) -> None:
        if transaccion_id is not None:
            _GLOBAL_ITEM_CACHE.pop(_remito_item_cache_key(transaccion_id), None)
            return
        _GLOBAL_ITEM_CACHE.clear()


def _remito_item_cache_key(transaccion_id: int) -> str:
    return f"{REMITO_PATH}/{transaccion_id}"
