from __future__ import annotations

from typing import Any
import httpx

from src.entities.schemas import ProductCreate, ProductOut, ProductUpdate
from src.interface_adapter.controller.api.app.settings import settings
from src.shared.logger import get_logger

BASE_URL = "https://xubio.com/API/1.1"
TOKEN_ENDPOINT = "https://xubio.com/API/1.1/TokenEndpoint"
PRODUCT_ENDPOINT = "/ProductoVentaBean"
UNIT_MEASURE_ENDPOINT = "/UnidadMedidaBean"


class RealXubioApiClient:
    def __init__(self) -> None:
        self._token: str | None = None
        self._client = httpx.Client(base_url=BASE_URL, timeout=20)
        self._logger = get_logger(__name__)

    def _get_token(self) -> str:
        if not settings.xubio_client_id or not settings.xubio_secret_id:
            raise ValueError("Faltan XUBIO_CLIENT_ID / XUBIO_SECRET_ID")
        self._logger.info("Solicitando token OAuth2.")
        response = httpx.post(
            TOKEN_ENDPOINT,
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
        self._logger.info("Token OAuth2 obtenido.")
        return token

    def _is_invalid_token(self, response: httpx.Response) -> bool:
        if response.status_code != 401:
            return False
        try:
            data = response.json()
        except ValueError:
            return False
        return data.get("error") == "invalid_token"

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        token = self._token or self._get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        response = self._client.request(method, url, headers=headers, **kwargs)
        if self._is_invalid_token(response):
            self._logger.warning("Token invalido, reintentando autenticacion.")
            token = self._get_token()
            headers["Authorization"] = f"Bearer {token}"
            response = self._client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    def create_product(self, payload: ProductCreate) -> ProductOut:
        # TODO: confirmar endpoint real de productos
        response = self._request("POST", PRODUCT_ENDPOINT, json=payload.model_dump())
        data = response.json()
        return ProductOut(**data)

    def update_product(self, external_id: str, payload: ProductUpdate) -> ProductOut:
        response = self._request(
            "PATCH",
            f"{PRODUCT_ENDPOINT}/{external_id}",
            json=payload.model_dump(exclude_none=True),
        )
        data = response.json()
        return ProductOut(**data)

    def delete_product(self, external_id: str) -> None:
        self._request("DELETE", f"{PRODUCT_ENDPOINT}/{external_id}")

    def get_product(self, external_id: str) -> ProductOut:
        response = self._request("GET", f"{PRODUCT_ENDPOINT}/{external_id}")
        data = response.json()
        return ProductOut(**data)

    def list_products(self, limit: int = 50, offset: int = 0) -> list[ProductOut]:
        response = self._request("GET", PRODUCT_ENDPOINT)
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
        price = item.get("precioVenta") or item.get("precioUltCompra") or item.get("price")
        return ProductOut(
            external_id=str(external_id),
            name=name,
            sku=sku,
            price=price,
        )

    def list_unit_measures(self) -> list[dict[str, Any]]:
        response = self._request("GET", UNIT_MEASURE_ENDPOINT)
        data = response.json()
        if isinstance(data, list):
            return data
        return []
