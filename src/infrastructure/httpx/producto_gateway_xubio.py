"""
Path: src/infrastructure/httpx/producto_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional, Tuple

import os
import time
import httpx

from ...use_cases.ports.producto_gateway import ProductoGateway
from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from .token_client import request_with_token

logger = get_logger(__name__)

_GLOBAL_LIST_CACHE: Optional[Tuple[float, List[Dict[str, Any]]]] = None


class XubioProductoGateway(ProductoGateway):
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
        items = self._fetch_list()
        self._store_cache(items)
        return items

    def get(self, producto_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/ProductoVentaBean/{producto_id}")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code == 404 or resp.status_code >= 500:
                logger.warning(
                    "Xubio GET %s failed with %s, falling back to list lookup",
                    url,
                    resp.status_code,
                )
                return self._fallback_get_from_list_or_compra(producto_id)
            _raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def _fetch_list(self) -> List[Dict[str, Any]]:
        url = self._url("/API/1.1/ProductoVentaBean")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code >= 500:
                logger.warning(
                    "Xubio GET %s failed with %s, falling back to ProductoCompraBean",
                    url,
                    resp.status_code,
                )
                return self._fallback_list_from_compra()
            return _extract_list(resp)
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
        logger.info("Xubio lista productos: cache hit (%d items)", len(items))
        return list(items)

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        if self._list_cache_ttl <= 0:
            return
        global _GLOBAL_LIST_CACHE
        _GLOBAL_LIST_CACHE = (time.time(), list(items))

    def _fallback_list_from_compra(self) -> List[Dict[str, Any]]:
        url = self._url("/API/1.1/ProductoCompraBean")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            return _extract_list(resp)
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def _fallback_get_from_list(self, producto_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_producto_id(item, producto_id):
                return item
        return None

    def _fallback_get_from_list_or_compra(self, producto_id: int) -> Optional[Dict[str, Any]]:
        item = self._fallback_get_from_list(producto_id)
        if item is not None:
            return item
        return self._fallback_get_from_compra(producto_id)

    def _fallback_get_from_compra(self, producto_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/ProductoCompraBean/{producto_id}")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code == 404:
                return None
            if resp.status_code >= 500:
                logger.warning(
                    "Xubio GET %s failed with %s, falling back to compra list lookup",
                    url,
                    resp.status_code,
                )
                return self._fallback_get_from_compra_list(producto_id)
            _raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def _fallback_get_from_compra_list(self, producto_id: int) -> Optional[Dict[str, Any]]:
        items = self._fallback_list_from_compra()
        for item in items:
            if _match_producto_id(item, producto_id):
                return item
        return None


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        raise ExternalServiceError(f"Xubio error {resp.status_code}: {resp.text}")


def _extract_list(resp: httpx.Response) -> List[Dict[str, Any]]:
    _raise_for_status(resp)
    payload = resp.json()
    if isinstance(payload, list):
        logger.info("Xubio lista productos: %d items (list)", len(payload))
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        logger.info("Xubio lista productos: %d items (items)", len(payload["items"]))
        return payload["items"]
    raise ExternalServiceError("Respuesta inesperada al listar productos")


def _match_producto_id(item: Dict[str, Any], producto_id: int) -> bool:
    for key in ("productoid", "productoId", "ID", "id"):
        value = item.get(key)
        if value == producto_id:
            return True
    return False


def _read_cache_ttl() -> float:
    raw = os.getenv("XUBIO_PRODUCTO_LIST_TTL", "").strip()
    if not raw:
        return 60.0
    try:
        value = float(raw)
    except ValueError:
        return 60.0
    return value
