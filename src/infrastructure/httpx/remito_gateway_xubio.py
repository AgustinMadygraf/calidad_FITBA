from typing import Any, Dict, List, Optional

import httpx

from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from ...use_cases.ports.remito_gateway import RemitoGateway
from .token_client import request_with_token

logger = get_logger(__name__)


class XubioRemitoGateway(RemitoGateway):
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = 10.0) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        url = self._url("/API/1.1/remitoVentaBean")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            return _extract_list(resp)
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def get(self, transaccion_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/remitoVentaBean/{transaccion_id}")
        try:
            resp = request_with_token("GET", url, timeout=self._timeout)
            logger.info("Xubio GET %s -> %s", url, resp.status_code)
            if resp.status_code == 404:
                return None
            _raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url("/API/1.1/remitoVentaBean")
        try:
            resp = request_with_token("POST", url, timeout=self._timeout, json=data)
            logger.info("Xubio POST %s -> %s", url, resp.status_code)
            _raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def update(self, transaccion_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/remitoVentaBean/{transaccion_id}")
        try:
            resp = request_with_token("PUT", url, timeout=self._timeout, json=data)
            logger.info("Xubio PUT %s -> %s", url, resp.status_code)
            if resp.status_code == 404:
                return None
            _raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def delete(self, transaccion_id: int) -> bool:
        url = self._url(f"/API/1.1/remitoVentaBean/{transaccion_id}")
        try:
            resp = request_with_token("DELETE", url, timeout=self._timeout)
            logger.info("Xubio DELETE %s -> %s", url, resp.status_code)
            if resp.status_code == 404:
                return False
            _raise_for_status(resp)
            return True
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        raise ExternalServiceError(f"Xubio error {resp.status_code}: {resp.text}")


def _extract_list(resp: httpx.Response) -> List[Dict[str, Any]]:
    _raise_for_status(resp)
    payload = resp.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ExternalServiceError("Respuesta inesperada al listar remitos")
