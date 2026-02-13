"""
Path: src/infrastructure/httpx/categoria_fiscal_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...shared.id_mapping import match_any_id
from ...shared.logger import get_logger
from ...use_cases.ports.categoria_fiscal_gateway import CategoriaFiscalGateway
from .cache_provider import providers_for_module
from .xubio_cache_helpers import (
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_crud_helpers import list_items

logger = get_logger(__name__)

CATEGORIA_FISCAL_PATH = "/API/1.1/categoriaFiscal"
CATEGORIA_FISCAL_ID_KEYS = ("ID", "id")
_LIST_CACHE_PROVIDER, _ = providers_for_module(
    namespace="categoria_fiscal", with_item_cache=False
)
# Compatibility alias for tests and debug tooling.
_GLOBAL_LIST_CACHE = _LIST_CACHE_PROVIDER.store


class XubioCategoriaFiscalGateway(CategoriaFiscalGateway):
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
            list_cache_ttl = read_cache_ttl("XUBIO_CATEGORIA_FISCAL_LIST_TTL")
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
        url = self._url(CATEGORIA_FISCAL_PATH)
        items = list_items(
            url=url,
            timeout=self._timeout,
            label="categorias_fiscales",
            logger=logger,
        )
        self._store_cache(items)
        return items

    def get(self, categoria_fiscal_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if match_any_id(item, categoria_fiscal_id, CATEGORIA_FISCAL_ID_KEYS):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached = _LIST_CACHE_PROVIDER.get(
            CATEGORIA_FISCAL_PATH, ttl=self._list_cache_ttl
        )
        if cached is not None:
            logger.info(
                "Xubio lista categorias fiscales: cache hit (%d items)",
                len(cached),
            )
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        _LIST_CACHE_PROVIDER.set(
            CATEGORIA_FISCAL_PATH,
            items,
            ttl=self._list_cache_ttl,
        )
