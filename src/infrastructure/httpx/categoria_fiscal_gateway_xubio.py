"""
Path: src/infrastructure/httpx/categoria_fiscal_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...shared.logger import get_logger
from ...use_cases.ports.categoria_fiscal_gateway import CategoriaFiscalGateway
from .xubio_crud_helpers import get_item_with_fallback, list_items

logger = get_logger(__name__)

CATEGORIA_FISCAL_PATH = "/API/1.1/categoriaFiscal"


class XubioCategoriaFiscalGateway(CategoriaFiscalGateway):
    def __init__(
        self, base_url: Optional[str] = None, timeout: Optional[float] = 10.0
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        url = self._url(CATEGORIA_FISCAL_PATH)
        return list_items(
            url=url,
            timeout=self._timeout,
            label="categorias_fiscales",
            logger=logger,
        )

    def get(self, categoria_fiscal_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"{CATEGORIA_FISCAL_PATH}/{categoria_fiscal_id}")
        item = get_item_with_fallback(
            url=url,
            timeout=self._timeout,
            logger=logger,
            fallback=lambda: self._fallback_get_from_list(categoria_fiscal_id),
        )
        if item is not None:
            return item
        return self._fallback_get_from_list(categoria_fiscal_id)

    def _fallback_get_from_list(self, categoria_fiscal_id: int) -> Optional[Dict[str, Any]]:
        items = self.list()
        for item in items:
            if _match_categoria_fiscal_id(item, categoria_fiscal_id):
                return item
        return None


def _match_categoria_fiscal_id(item: Dict[str, Any], categoria_fiscal_id: int) -> bool:
    for key in ("ID", "id"):
        value = item.get(key)
        if value == categoria_fiscal_id:
            return True
    return False
