"""
Path: src/infrastructure/httpx/cliente_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...use_cases.ports.cliente_gateway import ClienteGateway
from ...shared.logger import get_logger
from .cache_provider import providers_for_module
from .xubio_cache_helpers import (
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
from .xubio_cached_crud_gateway_base import XubioCachedCrudGatewayBase

logger = get_logger(__name__)

CLIENTE_PATH = "/API/1.1/clienteBean"
CLIENTE_ID_KEYS = ("cliente_id", "clienteId", "ID", "id")
_LIST_CACHE_PROVIDER, _ITEM_CACHE_PROVIDER = providers_for_module(
    namespace="cliente", with_item_cache=True
)
# Compatibility aliases for tests and debug tooling.
_GLOBAL_LIST_CACHE = _LIST_CACHE_PROVIDER.store
_GLOBAL_ITEM_CACHE = _ITEM_CACHE_PROVIDER.store


class XubioClienteGateway(XubioCachedCrudGatewayBase, ClienteGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
        enable_get_cache: Optional[bool] = None,
    ) -> None:
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_CLIENTE_LIST_TTL", default=30.0)
        if enable_get_cache is None:
            enable_get_cache = default_get_cache_enabled()
        if not enable_get_cache:
            list_cache_ttl = 0.0
        super().__init__(
            base_url=base_url or "https://xubio.com",
            timeout=float(timeout or 10.0),
            list_cache_ttl=float(list_cache_ttl),
            path=CLIENTE_PATH,
            list_label="clientes",
            detail_label="cliente",
            id_keys=CLIENTE_ID_KEYS,
            logger=logger,
            list_cache_provider=_LIST_CACHE_PROVIDER,
            item_cache_provider=_ITEM_CACHE_PROVIDER,
            prefer_list_lookup_before_detail=True,
        )

    def _fetch_list_remote(self) -> List[Dict[str, Any]]:
        return list_items(
            url=self._url(CLIENTE_PATH),
            timeout=self._timeout,
            label="clientes",
            logger=logger,
        )

    def _fetch_detail_remote(self, resource_id: int) -> Optional[Dict[str, Any]]:
        return get_item(
            url=self._url(f"{CLIENTE_PATH}/{resource_id}"),
            timeout=self._timeout,
            logger=logger,
        )

    def _create_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return create_item(
            url=self._url(CLIENTE_PATH),
            timeout=self._timeout,
            data=data,
            logger=logger,
        )

    def _update_remote(
        self, resource_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return update_item(
            url=self._url(f"{CLIENTE_PATH}/{resource_id}"),
            timeout=self._timeout,
            data=data,
            logger=logger,
        )

    def _delete_remote(self, resource_id: int) -> bool:
        return delete_item(
            url=self._url(f"{CLIENTE_PATH}/{resource_id}"),
            timeout=self._timeout,
            logger=logger,
        )

def _cliente_item_cache_key(cliente_id: int) -> str:
    return f"{CLIENTE_PATH}/{cliente_id}"
