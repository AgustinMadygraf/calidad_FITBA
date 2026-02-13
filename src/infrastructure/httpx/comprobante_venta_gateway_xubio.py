"""
Path: src/infrastructure/httpx/comprobante_venta_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

from ...shared.id_mapping import match_any_id
from ...shared.logger import get_logger
from ...use_cases.ports.comprobante_venta_gateway import ComprobanteVentaGateway
from .xubio_cache_helpers import (
    cache_get,
    cache_set,
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_crud_helpers import get_item_with_fallback, list_items

logger = get_logger(__name__)

COMPROBANTE_VENTA_PATH = "/API/1.1/comprobanteVentaBean"
COMPROBANTE_ID_KEYS = ("transaccionid", "transaccionId", "ID", "id")
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
_GLOBAL_ITEM_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


class XubioComprobanteVentaGateway(ComprobanteVentaGateway):
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
            list_cache_ttl = read_cache_ttl("XUBIO_COMPROBANTE_VENTA_LIST_TTL")
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
        url = self._url(COMPROBANTE_VENTA_PATH)
        items = list_items(
            url=url,
            timeout=self._timeout,
            label="comprobantes_venta",
            logger=logger,
        )
        self._store_list_cache(items)
        return items

    def get(self, comprobante_id: int) -> Optional[Dict[str, Any]]:
        cached_item = self._get_cached_item(comprobante_id)
        if cached_item is not None:
            logger.info(
                "Xubio comprobanteVenta detalle: cache hit (%s)",
                comprobante_id,
            )
            return cached_item

        url = self._url(f"{COMPROBANTE_VENTA_PATH}/{comprobante_id}")
        item = get_item_with_fallback(
            url=url,
            timeout=self._timeout,
            logger=logger,
            fallback=lambda: self._fallback_get_from_list(comprobante_id),
        )
        if item is not None:
            self._store_item_cache(comprobante_id, item)
        return item

    def _fallback_get_from_list(self, comprobante_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if match_any_id(item, comprobante_id, COMPROBANTE_ID_KEYS):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached = cache_get(
            _GLOBAL_LIST_CACHE,
            COMPROBANTE_VENTA_PATH,
            ttl=self._list_cache_ttl,
        )
        if cached is not None:
            logger.info(
                "Xubio lista comprobantes_venta: cache hit (%d items)",
                len(cached),
            )
        return cached

    def _store_list_cache(self, items: List[Dict[str, Any]]) -> None:
        cache_set(
            _GLOBAL_LIST_CACHE,
            COMPROBANTE_VENTA_PATH,
            items,
            ttl=self._list_cache_ttl,
        )

    def _get_cached_item(self, comprobante_id: int) -> Optional[Dict[str, Any]]:
        return cache_get(
            _GLOBAL_ITEM_CACHE,
            _comprobante_item_cache_key(comprobante_id),
            ttl=self._list_cache_ttl,
        )

    def _store_item_cache(self, comprobante_id: int, item: Dict[str, Any]) -> None:
        cache_set(
            _GLOBAL_ITEM_CACHE,
            _comprobante_item_cache_key(comprobante_id),
            item,
            ttl=self._list_cache_ttl,
        )


def _comprobante_item_cache_key(comprobante_id: int) -> str:
    return f"{COMPROBANTE_VENTA_PATH}/{comprobante_id}"
