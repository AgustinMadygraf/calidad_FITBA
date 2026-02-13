"""
Path: src/infrastructure/httpx/lista_precio_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...shared.logger import get_logger
from ...use_cases.ports.lista_precio_gateway import ListaPrecioGateway
from .cache_provider import providers_for_module
from .xubio_cache_helpers import (
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_crud_helpers import (
    create_item,
    delete_item,
    get_item_with_fallback,
    list_items,
    patch_item,
    update_item,
)
from .xubio_cached_crud_gateway_base import XubioCachedCrudGatewayBase

logger = get_logger(__name__)

LISTA_PRECIO_PATH = "/API/1.1/listaPrecioBean"
LISTA_PRECIO_ID_KEYS = ("listaPrecioID", "listaPrecioId", "ID", "id")
_LIST_CACHE_PROVIDER, _ITEM_CACHE_PROVIDER = providers_for_module(
    namespace="lista_precio", with_item_cache=True
)
# Compatibility aliases for tests and debug tooling.
_GLOBAL_LIST_CACHE = _LIST_CACHE_PROVIDER.store
_GLOBAL_ITEM_CACHE = _ITEM_CACHE_PROVIDER.store


class XubioListaPrecioGateway(XubioCachedCrudGatewayBase, ListaPrecioGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
        enable_get_cache: Optional[bool] = None,
    ) -> None:
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_LISTA_PRECIO_LIST_TTL")
        if enable_get_cache is None:
            enable_get_cache = default_get_cache_enabled()
        if not enable_get_cache:
            list_cache_ttl = 0.0
        super().__init__(
            base_url=base_url or "https://xubio.com",
            timeout=float(timeout or 10.0),
            list_cache_ttl=float(list_cache_ttl),
            path=LISTA_PRECIO_PATH,
            list_label="listas_precio",
            detail_label="listaPrecio",
            id_keys=LISTA_PRECIO_ID_KEYS,
            logger=logger,
            list_cache_provider=_LIST_CACHE_PROVIDER,
            item_cache_provider=_ITEM_CACHE_PROVIDER,
        )

    def _fetch_list_remote(self) -> List[Dict[str, Any]]:
        return list_items(
            url=self._url(LISTA_PRECIO_PATH),
            timeout=self._timeout,
            label="listas_precio",
            logger=logger,
        )

    def _fetch_detail_remote(self, resource_id: int) -> Optional[Dict[str, Any]]:
        return get_item_with_fallback(
            url=self._url(f"{LISTA_PRECIO_PATH}/{resource_id}"),
            timeout=self._timeout,
            logger=logger,
            fallback=lambda: self._fallback_get_from_list(resource_id),
        )

    def _create_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return create_item(
            url=self._url(LISTA_PRECIO_PATH),
            timeout=self._timeout,
            data=data,
            logger=logger,
        )

    def _update_remote(
        self, resource_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return update_item(
            url=self._url(f"{LISTA_PRECIO_PATH}/{resource_id}"),
            timeout=self._timeout,
            data=data,
            logger=logger,
        )

    def _patch_remote(
        self, resource_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return patch_item(
            url=self._url(f"{LISTA_PRECIO_PATH}/{resource_id}"),
            timeout=self._timeout,
            data=data,
            logger=logger,
        )

    def _delete_remote(self, resource_id: int) -> bool:
        return delete_item(
            url=self._url(f"{LISTA_PRECIO_PATH}/{resource_id}"),
            timeout=self._timeout,
            logger=logger,
        )


def _lista_precio_item_cache_key(lista_precio_id: int) -> str:
    return f"{LISTA_PRECIO_PATH}/{lista_precio_id}"
