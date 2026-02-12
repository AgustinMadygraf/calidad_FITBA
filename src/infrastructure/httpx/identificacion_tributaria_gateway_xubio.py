"""
Path: src/infrastructure/httpx/identificacion_tributaria_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

import time

from ...shared.logger import get_logger
from ...use_cases.ports.identificacion_tributaria_gateway import (
    IdentificacionTributariaGateway,
)
from .xubio_cache_helpers import read_cache_ttl
from .xubio_crud_helpers import list_items

logger = get_logger(__name__)

IDENTIFICACION_TRIBUTARIA_PATH = "/API/1.1/identificacionTributaria"
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class XubioIdentificacionTributariaGateway(IdentificacionTributariaGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl(
                "XUBIO_IDENTIFICACION_TRIBUTARIA_LIST_TTL"
            )
        self._list_cache_ttl = list_cache_ttl

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            return cached
        url = self._url(IDENTIFICACION_TRIBUTARIA_PATH)
        items = list_items(
            url=url,
            timeout=self._timeout,
            label="identificaciones_tributarias",
            logger=logger,
        )
        self._store_cache(items)
        return items

    def get(self, identificacion_tributaria_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_identificacion_tributaria_id(item, identificacion_tributaria_id):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached: Optional[List[Dict[str, Any]]] = None
        if self._list_cache_ttl > 0:
            entry = _GLOBAL_LIST_CACHE.get(IDENTIFICACION_TRIBUTARIA_PATH)
            if entry is not None:
                timestamp, items = entry
                if time.time() - timestamp <= self._list_cache_ttl:
                    logger.info(
                        "Xubio lista identif. tributarias: cache hit (%d items)",
                        len(items),
                    )
                    cached = list(items)
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        if self._list_cache_ttl <= 0:
            return
        _GLOBAL_LIST_CACHE[IDENTIFICACION_TRIBUTARIA_PATH] = (
            time.time(),
            list(items),
        )


def _match_identificacion_tributaria_id(
    item: Dict[str, Any], identificacion_tributaria_id: int
) -> bool:
    for key in ("ID", "id"):
        value = item.get(key)
        if value == identificacion_tributaria_id:
            return True
    return False
