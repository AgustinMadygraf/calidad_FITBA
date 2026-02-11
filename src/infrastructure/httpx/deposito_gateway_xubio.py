"""
Path: src/infrastructure/httpx/deposito_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

import time
import httpx

from ...use_cases.ports.deposito_gateway import DepositoGateway
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .token_client import request_with_token
from .xubio_cache_helpers import read_cache_ttl
from .xubio_httpx_helpers import extract_list, raise_for_status

logger = get_logger(__name__)

DEPOSITO_PATH = "/API/1.1/depositos"
_GLOBAL_LIST_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}


class XubioDepositoGateway(DepositoGateway):
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 10.0,
        list_cache_ttl: Optional[float] = None,
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout
        if list_cache_ttl is None:
            list_cache_ttl = read_cache_ttl("XUBIO_DEPOSITO_LIST_TTL")
        self._list_cache_ttl = list_cache_ttl

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            return cached
        url = self._url(DEPOSITO_PATH)
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            items = extract_list(resp, label="depositos")
            logger.info("Xubio lista depositos: %d items", len(items))
            self._store_cache(items)
            return items
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def get(self, deposito_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"{DEPOSITO_PATH}/{deposito_id}")
        result: Optional[Dict[str, Any]] = None
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code == 404 or resp.status_code >= 500:
                logger.warning(
                    "Xubio GET %s failed with %s, falling back to list lookup",
                    url,
                    resp.status_code,
                )
                result = self._fallback_get_from_list(deposito_id)
            else:
                raise_for_status(resp)
                result = resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc
        return result

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached: Optional[List[Dict[str, Any]]] = None
        if self._list_cache_ttl > 0:
            entry = _GLOBAL_LIST_CACHE.get(DEPOSITO_PATH)
            if entry is not None:
                timestamp, items = entry
                if time.time() - timestamp <= self._list_cache_ttl:
                    logger.info(
                        "Xubio lista depositos: cache hit (%d items)", len(items)
                    )
                    cached = list(items)
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        if self._list_cache_ttl <= 0:
            return
        _GLOBAL_LIST_CACHE[DEPOSITO_PATH] = (time.time(), list(items))

    def _fallback_get_from_list(self, deposito_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_deposito_id(item, deposito_id):
                return item
        return None


def _match_deposito_id(item: Dict[str, Any], deposito_id: int) -> bool:
    for key in ("ID", "id", "depositoId"):
        value = item.get(key)
        if value == deposito_id:
            return True
    return False
