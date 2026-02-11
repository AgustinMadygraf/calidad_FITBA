from typing import Any, Dict, List, Optional

import httpx

from ...shared.logger import get_logger
from ...use_cases.errors import ExternalServiceError
from ...use_cases.ports.remito_gateway import RemitoGateway
from .token_client import request_with_token
from .xubio_crud_helpers import create_item, delete_item, list_items, update_item
from .xubio_httpx_helpers import extract_list, raise_for_status

logger = get_logger(__name__)


class XubioRemitoGateway(RemitoGateway):
    def __init__(
        self, base_url: Optional[str] = None, timeout: Optional[float] = 10.0
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        url = self._url("/API/1.1/remitoVentaBean")
        return list_items(
            url=url, timeout=self._timeout, label="remitos", logger=logger
        )

    def get(self, transaccion_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/remitoVentaBean/{transaccion_id}")
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
                return self._fallback_get_from_list(transaccion_id)
            raise_for_status(resp)
            return resp.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(str(exc)) from exc

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url("/API/1.1/remitoVentaBean")
        return create_item(url=url, timeout=self._timeout, data=data, logger=logger)

    def update(
        self, transaccion_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/remitoVentaBean/{transaccion_id}")
        return update_item(url=url, timeout=self._timeout, data=data, logger=logger)

    def delete(self, transaccion_id: int) -> bool:
        url = self._url(f"/API/1.1/remitoVentaBean/{transaccion_id}")
        return delete_item(url=url, timeout=self._timeout, logger=logger)

    def _fallback_get_from_list(self, transaccion_id: int) -> Optional[Dict[str, Any]]:
        url = self._url("/API/1.1/remitoVentaBean")
        resp = request_with_token("GET", url, timeout=self._timeout)
        logger.info("Xubio GET %s -> %s", url, resp.status_code)
        items = extract_list(resp, label="remitos")
        for item in items:
            if item.get("transaccionId") == transaccion_id:
                return item
        return None
