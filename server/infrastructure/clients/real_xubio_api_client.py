from __future__ import annotations

from typing import Any
import httpx

from shared.schemas import ProductCreate, ProductOut, ProductUpdate
from server.app.settings import settings


class RealXubioApiClient:
    def __init__(self) -> None:
        self._token: str | None = None
        self._client = httpx.Client(base_url=settings.xubio_base_url, timeout=20)

    def _get_token(self) -> str:
        if not settings.xubio_client_id or not settings.xubio_secret_id:
            raise ValueError("Faltan XUBIO_CLIENT_ID / XUBIO_SECRET_ID")
        response = httpx.post(
            settings.xubio_token_endpoint,
            data={"grant_type": "client_credentials"},
            auth=httpx.BasicAuth(settings.xubio_client_id, settings.xubio_secret_id),
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if not token:
            raise ValueError("No se obtuvo access_token")
        self._token = token
        return token

    def _is_invalid_token(self, response: httpx.Response) -> bool:
        if response.status_code != 401:
            return False
        try:
            data = response.json()
        except Exception:
            return False
        return data.get("error") == "invalid_token"

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        token = self._token or self._get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        response = self._client.request(method, url, headers=headers, **kwargs)
        if self._is_invalid_token(response):
            token = self._get_token()
            headers["Authorization"] = f"Bearer {token}"
            response = self._client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def create_product(self, payload: ProductCreate) -> ProductOut:
        # TODO: confirmar endpoint real de productos
        response = self._request("POST", settings.xubio_product_endpoint, json=payload.model_dump())
        data = response.json()
        return ProductOut(**data)

    def update_product(self, external_id: str, payload: ProductUpdate) -> ProductOut:
        response = self._request(
            "PUT",
            f"{settings.xubio_product_endpoint}/{external_id}",
            json=payload.model_dump(exclude_none=True),
        )
        data = response.json()
        return ProductOut(**data)

    def delete_product(self, external_id: str) -> None:
        self._request("DELETE", f"{settings.xubio_product_endpoint}/{external_id}")

    def get_product(self, external_id: str) -> ProductOut:
        response = self._request("GET", f"{settings.xubio_product_endpoint}/{external_id}")
        data = response.json()
        return ProductOut(**data)

    def list_products(self, limit: int = 50, offset: int = 0) -> list[ProductOut]:
        response = self._request("GET", settings.xubio_product_endpoint)
        data = response.json()
        return [self._map_product(item) for item in data]

    def _map_product(self, item: dict[str, Any]) -> ProductOut:
        external_id = (
            item.get("productoid")
            or item.get("productoId")
            or item.get("id")
            or item.get("external_id")
        )
        name = item.get("nombre") or item.get("name") or item.get("descripcion") or "SIN_NOMBRE"
        sku = item.get("codigo") or item.get("sku")
        price = item.get("precioVenta") or item.get("price")
        return ProductOut(
            external_id=str(external_id),
            name=name,
            sku=sku,
            price=price,
        )
