"""
Path: src/infrastructure/httpx/identificacion_tributaria_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...shared.logger import get_logger
from ...use_cases.ports.identificacion_tributaria_gateway import (
    IdentificacionTributariaGateway,
)
from .xubio_crud_helpers import get_item_with_fallback, list_items

logger = get_logger(__name__)

IDENTIFICACION_TRIBUTARIA_PATH = "/API/1.1/identificacionTributaria"


class XubioIdentificacionTributariaGateway(IdentificacionTributariaGateway):
    def __init__(
        self, base_url: Optional[str] = None, timeout: Optional[float] = 10.0
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        url = self._url(IDENTIFICACION_TRIBUTARIA_PATH)
        return list_items(
            url=url,
            timeout=self._timeout,
            label="identificaciones_tributarias",
            logger=logger,
        )

    def get(self, identificacion_tributaria_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(
            f"{IDENTIFICACION_TRIBUTARIA_PATH}/{identificacion_tributaria_id}"
        )
        item = get_item_with_fallback(
            url=url,
            timeout=self._timeout,
            logger=logger,
            fallback=lambda: self._fallback_get_from_list(identificacion_tributaria_id),
        )
        if item is not None:
            return item
        return self._fallback_get_from_list(identificacion_tributaria_id)

    def _fallback_get_from_list(
        self, identificacion_tributaria_id: int
    ) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_identificacion_tributaria_id(item, identificacion_tributaria_id):
                return item
        return None


def _match_identificacion_tributaria_id(
    item: Dict[str, Any], identificacion_tributaria_id: int
) -> bool:
    for key in ("ID", "id"):
        value = item.get(key)
        if value == identificacion_tributaria_id:
            return True
    return False
