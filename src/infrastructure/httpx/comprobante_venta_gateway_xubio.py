"""
Path: src/infrastructure/httpx/comprobante_venta_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...shared.logger import get_logger
from ...use_cases.ports.comprobante_venta_gateway import ComprobanteVentaGateway
from .cache_provider import providers_for_module
from .xubio_cache_helpers import (
    default_get_cache_enabled,
    read_cache_ttl,
)
from .xubio_crud_helpers import get_item_with_fallback, list_items
from .xubio_cached_crud_gateway_base import XubioCachedCrudGatewayBase

logger = get_logger(__name__)

COMPROBANTE_VENTA_PATH = "/API/1.1/comprobanteVentaBean"
COMPROBANTE_ID_KEYS = ("transaccionid", "transaccionId", "ID", "id")
_LIST_CACHE_PROVIDER, _ITEM_CACHE_PROVIDER = providers_for_module(
    namespace="comprobante_venta", with_item_cache=True
)
# Compatibility aliases for tests and debug tooling.
_GLOBAL_LIST_CACHE = _LIST_CACHE_PROVIDER.store
_GLOBAL_ITEM_CACHE = _ITEM_CACHE_PROVIDER.store


class XubioComprobanteVentaGateway(XubioCachedCrudGatewayBase, ComprobanteVentaGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
        enable_get_cache: Optional[bool] = None,
    ) -> None:
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_COMPROBANTE_VENTA_LIST_TTL")
        if enable_get_cache is None:
            enable_get_cache = default_get_cache_enabled()
        if not enable_get_cache:
            list_cache_ttl = 0.0
        super().__init__(
            base_url=base_url or "https://xubio.com",
            timeout=float(timeout or 10.0),
            list_cache_ttl=float(list_cache_ttl),
            path=COMPROBANTE_VENTA_PATH,
            list_label="comprobantes_venta",
            detail_label="comprobanteVenta",
            id_keys=COMPROBANTE_ID_KEYS,
            logger=logger,
            list_cache_provider=_LIST_CACHE_PROVIDER,
            item_cache_provider=_ITEM_CACHE_PROVIDER,
        )

    def _fetch_list_remote(self) -> List[Dict[str, Any]]:
        return list_items(
            url=self._url(COMPROBANTE_VENTA_PATH),
            timeout=self._timeout,
            label="comprobantes_venta",
            logger=logger,
        )

    def _fetch_detail_remote(self, resource_id: int) -> Optional[Dict[str, Any]]:
        return get_item_with_fallback(
            url=self._url(f"{COMPROBANTE_VENTA_PATH}/{resource_id}"),
            timeout=self._timeout,
            logger=logger,
            fallback=lambda: self._fallback_get_from_list(resource_id),
        )


def _comprobante_item_cache_key(comprobante_id: int) -> str:
    return f"{COMPROBANTE_VENTA_PATH}/{comprobante_id}"
