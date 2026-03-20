from typing import Any, Dict, List, Optional

import httpx

from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from ...use_cases.ports.remito_gateway import RemitoGateway
from .cache_provider import providers_for_module
from .xubio_cache_helpers import (
    default_get_cache_enabled,
    read_cache_ttl,
)
from .token_client import request_with_token
from .xubio_crud_helpers import create_item, delete_item, list_items, update_item
from .xubio_cached_crud_gateway_base import XubioCachedCrudGatewayBase
from .xubio_httpx_helpers import raise_for_status

logger = get_logger(__name__)

REMITO_PATH = "/API/1.1/remitoVentaBean"
REMITO_ID_KEYS = ("transaccionId",)
_LIST_CACHE_PROVIDER, _ITEM_CACHE_PROVIDER = providers_for_module(
    namespace="remito", with_item_cache=True
)
# Compatibility aliases for tests and debug tooling.
_GLOBAL_LIST_CACHE = _LIST_CACHE_PROVIDER.store
_GLOBAL_ITEM_CACHE = _ITEM_CACHE_PROVIDER.store


class XubioRemitoGateway(XubioCachedCrudGatewayBase, RemitoGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
        enable_get_cache: Optional[bool] = None,
    ) -> None:
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_REMITO_LIST_TTL", default=15.0)
        if enable_get_cache is None:
            enable_get_cache = default_get_cache_enabled()
        if not enable_get_cache:
            list_cache_ttl = 0.0
        super().__init__(
            base_url=base_url or "https://xubio.com",
            timeout=float(timeout or 10.0),
            list_cache_ttl=float(list_cache_ttl),
            path=REMITO_PATH,
            list_label="remitos",
            detail_label="remito",
            id_keys=REMITO_ID_KEYS,
            logger=logger,
            list_cache_provider=_LIST_CACHE_PROVIDER,
            item_cache_provider=_ITEM_CACHE_PROVIDER,
            prefer_list_lookup_before_detail=True,
        )

    def _fetch_list_remote(self) -> List[Dict[str, Any]]:
        return list_items(
            url=self._url(REMITO_PATH),
            timeout=self._timeout,
            label="remitos",
            logger=logger,
        )

    def _fetch_detail_remote(self, resource_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"{REMITO_PATH}/{resource_id}")
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
                return self._fallback_get_from_list(resource_id)
            raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def _create_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return create_item(
            url=self._url(REMITO_PATH),
            timeout=self._timeout,
            data=data,
            logger=logger,
        )

    def _update_remote(
        self, resource_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        payload = dict(data)
        payload["transaccionId"] = resource_id
        return update_item(
            url=self._url(REMITO_PATH),
            timeout=self._timeout,
            data=payload,
            logger=logger,
        )

    def _delete_remote(self, resource_id: int) -> bool:
        return delete_item(
            url=self._url(f"{REMITO_PATH}/{resource_id}"),
            timeout=self._timeout,
            logger=logger,
        )


def _remito_item_cache_key(transaccion_id: int) -> str:
    return f"{REMITO_PATH}/{transaccion_id}"
