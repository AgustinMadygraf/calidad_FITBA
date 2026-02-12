"""
Path: src/infrastructure/httpx/producto_gateway_xubio.py
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import httpx

from ...use_cases.ports.producto_gateway import ProductoGateway
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .token_client import request_with_token
from .xubio_crud_helpers import create_item, delete_item, update_item
from .xubio_cache_helpers import (
    cache_get,
    cache_set,
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_httpx_helpers import extract_list, raise_for_status

logger = get_logger(__name__)

DEFAULT_PRIMARY_BEAN = "ProductoVentaBean"
DEFAULT_FALLBACK_BEAN = "ProductoCompraBean"

_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
_GLOBAL_ITEM_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


@dataclass(frozen=True)
class ProductoGatewayConfig:
    primary_bean: str = DEFAULT_PRIMARY_BEAN
    fallback_bean: Optional[str] = DEFAULT_FALLBACK_BEAN


class XubioProductoGateway(ProductoGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        config: Optional[ProductoGatewayConfig] = None,
        list_cache_ttl: Optional[float] = None,
        enable_get_cache: Optional[bool] = None,
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout
        if config is None:
            config = ProductoGatewayConfig()
        self._primary_bean = config.primary_bean
        fallback_bean = config.fallback_bean
        if fallback_bean == self._primary_bean:
            fallback_bean = None
        self._fallback_bean = fallback_bean
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_PRODUCTO_LIST_TTL")
        if enable_get_cache is None:
            enable_get_cache = default_get_cache_enabled()
        if not enable_get_cache:
            list_cache_ttl = 0.0
        self._list_cache_ttl = max(0.0, float(list_cache_ttl))

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        return self._list_with_fallback(self._primary_bean, self._fallback_bean)

    def get(self, producto_id: int) -> Optional[Dict[str, Any]]:
        cached_item = self._get_cached_item(self._primary_bean, producto_id)
        if cached_item is not None:
            logger.info(
                "Xubio producto detalle: cache hit (%s:%s)",
                self._primary_bean,
                producto_id,
            )
            return cached_item
        if self._fallback_bean is not None:
            cached_item = self._get_cached_item(self._fallback_bean, producto_id)
            if cached_item is not None:
                logger.info(
                    "Xubio producto detalle: cache hit (%s:%s)",
                    self._fallback_bean,
                    producto_id,
                )
                return cached_item
        result: Optional[Dict[str, Any]] = None
        cached = self._get_cached_list(self._primary_bean)
        if cached is not None:
            for item in cached:
                if _match_producto_id(item, producto_id):
                    self._store_item_cache(self._primary_bean, producto_id, item)
                    return item
        status, item = self._get_from_bean(self._primary_bean, producto_id)
        if status == "ok":
            self._store_item_cache(self._primary_bean, producto_id, item)
            result = item
        else:
            result = self._find_in_list(
                self._primary_bean, self._fallback_bean, producto_id
            )
            if result is not None:
                self._store_item_cache(self._primary_bean, producto_id, result)
            if result is None and self._fallback_bean is not None:
                status, item = self._get_from_bean(self._fallback_bean, producto_id)
                if status == "ok":
                    self._store_item_cache(self._fallback_bean, producto_id, item)
                    result = item
                else:
                    result = self._find_in_list(self._fallback_bean, None, producto_id)
                    if result is not None:
                        self._store_item_cache(
                            self._fallback_bean, producto_id, result
                        )
        return result

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(f"/API/1.1/{self._primary_bean}")
        created = create_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache(self._primary_bean)
        self._clear_item_cache(self._primary_bean)
        return created

    def update(self, producto_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/{self._primary_bean}/{producto_id}")
        updated = update_item(url=url, timeout=self._timeout, data=data, logger=logger)
        self._clear_list_cache(self._primary_bean)
        self._clear_item_cache(self._primary_bean, producto_id)
        return updated

    def delete(self, producto_id: int) -> bool:
        url = self._url(f"/API/1.1/{self._primary_bean}/{producto_id}")
        deleted = delete_item(url=url, timeout=self._timeout, logger=logger)
        if deleted:
            self._clear_list_cache(self._primary_bean)
            self._clear_item_cache(self._primary_bean, producto_id)
        return deleted

    def _list_with_fallback(
        self, primary_bean: str, fallback_bean: Optional[str]
    ) -> List[Dict[str, Any]]:
        cached = self._get_cached_list(primary_bean)
        if cached is not None:
            return cached
        items, used_bean = self._fetch_list_with_fallback(primary_bean, fallback_bean)
        self._store_cache(primary_bean, items)
        if used_bean != primary_bean:
            self._store_cache(used_bean, items)
        return items

    def _fetch_list_with_fallback(
        self, bean: str, fallback_bean: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], str]:
        url = self._url(f"/API/1.1/{bean}")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code >= 500 and fallback_bean:
                logger.warning(
                    "Xubio GET %s failed with %s, falling back to %s",
                    url,
                    resp.status_code,
                    fallback_bean,
                )
                return self._fetch_list_with_fallback(fallback_bean, None)
            items = extract_list(resp, label="productos")
            logger.info("Xubio lista productos: %d items", len(items))
            return items, bean
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def _get_cached_list(self, bean: str) -> Optional[List[Dict[str, Any]]]:
        cached = cache_get(_GLOBAL_LIST_CACHE, bean, ttl=self._list_cache_ttl)
        if cached is not None:
            logger.info("Xubio lista productos: cache hit (%d items)", len(cached))
        return cached

    def _store_cache(self, bean: str, items: List[Dict[str, Any]]) -> None:
        cache_set(_GLOBAL_LIST_CACHE, bean, items, ttl=self._list_cache_ttl)
        for item in items:
            producto_id = _extract_producto_id(item)
            if producto_id is not None:
                self._store_item_cache(bean, producto_id, item)

    def _get_from_bean(
        self, bean: str, producto_id: int
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        url = self._url(f"/API/1.1/{bean}/{producto_id}")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code == 404:
                return "not_found", None
            if resp.status_code >= 500:
                logger.warning(
                    "Xubio GET %s failed with %s",
                    url,
                    resp.status_code,
                )
                return "error", None
            raise_for_status(resp)
            return "ok", resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def _find_in_list(
        self, bean: str, fallback_bean: Optional[str], producto_id: int
    ) -> Optional[Dict[str, Any]]:
        items = self._list_with_fallback(bean, fallback_bean)
        for item in items:
            if _match_producto_id(item, producto_id):
                return item
        return None

    def _get_cached_item(
        self, bean: str, producto_id: int
    ) -> Optional[Dict[str, Any]]:
        return cache_get(
            _GLOBAL_ITEM_CACHE,
            _producto_item_cache_key(bean, producto_id),
            ttl=self._list_cache_ttl,
        )

    def _store_item_cache(
        self, bean: str, producto_id: int, item: Optional[Dict[str, Any]]
    ) -> None:
        if item is None:
            return
        cache_set(
            _GLOBAL_ITEM_CACHE,
            _producto_item_cache_key(bean, producto_id),
            item,
            ttl=self._list_cache_ttl,
        )

    def _clear_list_cache(self, bean: str) -> None:
        _GLOBAL_LIST_CACHE.pop(bean, None)

    def _clear_item_cache(self, bean: str, producto_id: Optional[int] = None) -> None:
        if producto_id is not None:
            _GLOBAL_ITEM_CACHE.pop(_producto_item_cache_key(bean, producto_id), None)
            return
        keys = [key for key in _GLOBAL_ITEM_CACHE if key.startswith(f"/API/1.1/{bean}/")]
        for key in keys:
            _GLOBAL_ITEM_CACHE.pop(key, None)


def _match_producto_id(item: Dict[str, Any], producto_id: int) -> bool:
    for key in ("productoid", "productoId", "ID", "id"):
        value = item.get(key)
        if value == producto_id:
            return True
    return False


def _extract_producto_id(item: Dict[str, Any]) -> Optional[int]:
    for key in ("productoid", "productoId", "ID", "id"):
        value = item.get(key)
        if isinstance(value, int):
            return value
    return None


def _producto_item_cache_key(bean: str, producto_id: int) -> str:
    return f"/API/1.1/{bean}/{producto_id}"
