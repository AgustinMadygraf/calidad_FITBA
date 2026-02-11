"""
Path: src/infrastructure/httpx/deposito_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

import os
import time
import httpx

from ...use_cases.ports.deposito_gateway import DepositoGateway
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .token_client import request_with_token

logger = get_logger(__name__)

DEPOSITO_PATH = "/API/1.1/depositos"
_GLOBAL_LIST_CACHE: Optional[Tuple[float, List[Dict[str, Any]]]] = None


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
            list_cache_ttl = _read_cache_ttl()
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
            items = _extract_list(resp)
            self._store_cache(items)
            return items
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def get(self, deposito_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"{DEPOSITO_PATH}/{deposito_id}")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code == 404 or resp.status_code >= 500:
                logger.warning(
                    "Xubio GET %s failed with %s, falling back to list lookup",
                    url,
                    resp.status_code,
                )
                return self._fallback_get_from_list(deposito_id)
            _raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        global _GLOBAL_LIST_CACHE
        if _GLOBAL_LIST_CACHE is None:
            return None
        if self._list_cache_ttl <= 0:
            return None
        timestamp, items = _GLOBAL_LIST_CACHE
        if time.time() - timestamp > self._list_cache_ttl:
            return None
        logger.info("Xubio lista depositos: cache hit (%d items)", len(items))
        return list(items)

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        if self._list_cache_ttl <= 0:
            return
        global _GLOBAL_LIST_CACHE
        _GLOBAL_LIST_CACHE = (time.time(), list(items))

    def _fallback_get_from_list(self, deposito_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_deposito_id(item, deposito_id):
                return item
        return None


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        raise ExternalServiceError(f"Xubio error {resp.status_code}: {resp.text}")


def _extract_list(resp: httpx.Response) -> List[Dict[str, Any]]:
    _raise_for_status(resp)
    payload = resp.json()
    if isinstance(payload, list):
        logger.info("Xubio lista depositos: %d items (list)", len(payload))
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        logger.info("Xubio lista depositos: %d items (items)", len(payload["items"]))
        return payload["items"]
    raise ExternalServiceError("Respuesta inesperada al listar depositos")


def _match_deposito_id(item: Dict[str, Any], deposito_id: int) -> bool:
    for key in ("ID", "id", "depositoId"):
        value = item.get(key)
        if value == deposito_id:
            return True
    return False


def _read_cache_ttl() -> float:
    raw = os.getenv("XUBIO_DEPOSITO_LIST_TTL", "").strip()
    if not raw:
        return 60.0
    try:
        value = float(raw)
    except ValueError:
        return 60.0
    return value
