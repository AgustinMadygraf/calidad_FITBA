"""
Path: src/infrastructure/httpx/cliente_gateway_xubio.py
"""

from typing import Any, Dict, List, Optional

from ...use_cases.ports.cliente_gateway import ClienteGateway
from ...shared.logger import get_logger
from .xubio_crud_helpers import (
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)

logger = get_logger(__name__)


class XubioClienteGateway(ClienteGateway):
    def __init__(
        self, base_url: Optional[str] = None, timeout: Optional[float] = 10.0
    ) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        url = self._url("/API/1.1/clienteBean")
        return list_items(
            url=url, timeout=self._timeout, label="clientes", logger=logger
        )

    def get(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/clienteBean/{cliente_id}")
        return get_item(url=url, timeout=self._timeout, logger=logger)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url("/API/1.1/clienteBean")
        return create_item(url=url, timeout=self._timeout, data=data, logger=logger)

    def update(self, cliente_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/clienteBean/{cliente_id}")
        return update_item(url=url, timeout=self._timeout, data=data, logger=logger)

    def delete(self, cliente_id: int) -> bool:
        url = self._url(f"/API/1.1/clienteBean/{cliente_id}")
        return delete_item(url=url, timeout=self._timeout, logger=logger)
