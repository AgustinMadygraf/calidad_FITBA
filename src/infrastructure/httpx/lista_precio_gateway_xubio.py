"""
Path: src/infrastructure/httpx/lista_precio_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...shared.logger import get_logger
from ...use_cases.ports.lista_precio_gateway import ListaPrecioGateway
from .xubio_crud_helpers import get_item_with_fallback, list_items

logger = get_logger(__name__)


class XubioListaPrecioGateway(ListaPrecioGateway):
    def __init__(
        self, base_url: Optional[str] = None, timeout: Optional[float] = 10.0
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        url = self._url("/API/1.1/listaPrecioBean")
        return list_items(
            url=url, timeout=self._timeout, label="listas_precio", logger=logger
        )

    def get(self, lista_precio_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/listaPrecioBean/{lista_precio_id}")
        return get_item_with_fallback(
            url=url,
            timeout=self._timeout,
            logger=logger,
            fallback=lambda: self._fallback_get_from_list(lista_precio_id),
        )

    def _fallback_get_from_list(self, lista_precio_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_lista_precio_id(item, lista_precio_id):
                return item
        return None


def _match_lista_precio_id(item: Dict[str, Any], lista_precio_id: int) -> bool:
    for key in ("listaPrecioID", "listaPrecioId", "ID", "id"):
        value = item.get(key)
        if value == lista_precio_id:
            return True
    return False
