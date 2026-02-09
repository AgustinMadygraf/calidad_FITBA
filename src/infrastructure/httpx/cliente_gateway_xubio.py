from typing import Any, Dict, List, Optional

import httpx

from ...interface_adapter.gateways.cliente_gateway import ClienteGateway
from .token_client import request_with_token


class XubioClienteGateway(ClienteGateway):
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = 10.0) -> None:
        self._base_url = (base_url or "https://xubio.com").rstrip("/")
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        url = self._url("/API/1.1/clienteBean")
        resp = request_with_token("GET", url, timeout=self._timeout)
        return _extract_list(resp)

    def get(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/clienteBean/{cliente_id}")
        resp = request_with_token("GET", url, timeout=self._timeout)
        if resp.status_code == 404:
            return None
        _raise_for_status(resp)
        return resp.json()

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url("/API/1.1/clienteBean")
        resp = request_with_token("POST", url, timeout=self._timeout, json=data)
        _raise_for_status(resp)
        return resp.json()

    def update(self, cliente_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = self._url(f"/API/1.1/clienteBean/{cliente_id}")
        resp = request_with_token("PUT", url, timeout=self._timeout, json=data)
        if resp.status_code == 404:
            return None
        _raise_for_status(resp)
        return resp.json()

    def delete(self, cliente_id: int) -> bool:
        url = self._url(f"/API/1.1/clienteBean/{cliente_id}")
        resp = request_with_token("DELETE", url, timeout=self._timeout)
        if resp.status_code == 404:
            return False
        _raise_for_status(resp)
        return True


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        raise RuntimeError(f"Xubio error {resp.status_code}: {resp.text}")


def _extract_list(resp: httpx.Response) -> List[Dict[str, Any]]:
    _raise_for_status(resp)
    payload = resp.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise RuntimeError("Respuesta inesperada al listar clientes")
