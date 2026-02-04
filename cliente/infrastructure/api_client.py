"""
Path: cliente/infrastructure/api_client.py
"""

import os
import httpx
from cliente.dtos.contact_dto import ContactDTO

HARD_CODED_NGROK_URL = "subdominio.ngrok-free.app" # Sólo para build local sin .env


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class ApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        ngrok = os.getenv("NGROK_URL") or HARD_CODED_NGROK_URL
        port = os.getenv("API_PORT", "8000")
        if ngrok:
            default_base = f"https://{ngrok}"
        else:
            default_base = f"http://localhost:{port}"
        self.base_url = base_url or default_base
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def create_contact(self, payload: dict) -> ContactDTO:
        r = self._request("post", "/api/v1/contacts", json=payload)
        return self._handle_contact(r)

    def update_contact(self, contact_id: int, payload: dict) -> ContactDTO:
        r = self._request("put", f"/api/v1/contacts/{contact_id}", json=payload)
        return self._handle_contact(r)

    def delete_contact(self, contact_id: int) -> None:
        r = self._request("delete", f"/api/v1/contacts/{contact_id}")
        if r.status_code != 204:
            self._raise(r)

    def get_contact(self, contact_id: int) -> ContactDTO:
        r = self._request("get", f"/api/v1/contacts/{contact_id}")
        return self._handle_contact(r)

    def list_contacts(self, limit: int = 10, offset: int = 0) -> list[ContactDTO]:
        r = self._request("get", "/api/v1/contacts", params={"limit": limit, "offset": offset})
        if r.status_code != 200:
            self._raise(r)
        return [ContactDTO(**item) for item in r.json()["items"]]

    def search_contacts(self, query: str, limit: int = 50, offset: int = 0) -> list[ContactDTO]:
        r = self._request(
            "get", "/api/v1/contacts", params={"q": query, "limit": limit, "offset": offset}
        )
        if r.status_code != 200:
            self._raise(r)
        return [ContactDTO(**item) for item in r.json()["items"]]

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            return self._client.request(method, url, **kwargs)
        except httpx.ConnectError as exc:
            raise ApiError(0, f"No se pudo conectar a la API ({self.base_url})") from exc
        except httpx.RequestError as exc:
            raise ApiError(0, "Error de red al conectar con la API") from exc

    def _handle_contact(self, r: httpx.Response) -> ContactDTO:
        if r.status_code not in (200, 201):
            self._raise(r)
        return ContactDTO(**r.json())

    def _raise(self, r: httpx.Response) -> None:
        content_type = r.headers.get("content-type", "")
        if "text/html" in content_type:
            text = r.text or ""
            if "ERR_NGROK_3200" in text:
                raise ApiError(
                    r.status_code,
                    "El túnel de ngrok está offline. Ejecutá run_ngrok_tunnel.py y reintentá.",
                )
            raise ApiError(r.status_code, "Respuesta HTML inesperada desde la API")
        try:
            detail = r.json().get("detail", r.text)
        except (ValueError, AttributeError):
            detail = r.text
        raise ApiError(r.status_code, detail)
