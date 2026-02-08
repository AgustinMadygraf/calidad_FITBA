from __future__ import annotations

from typing import Any
import httpx


BASE_URL = "https://xubio.com/API/1.1"
TOKEN_ENDPOINT = "https://xubio.com/API/1.1/TokenEndpoint"
PRODUCT_ENDPOINT = "/ProductoVentaBean"
UNIT_MEASURE_ENDPOINT = "/UnidadMedidaBean"


class RealXubioClient:
    def __init__(self, client_id: str, secret_id: str) -> None:
        self._client_id = client_id
        self._secret_id = secret_id
        self._token: str | None = None
        self._client = httpx.Client(base_url=BASE_URL, timeout=20)

    def _get_token(self) -> str:
        response = httpx.post(
            TOKEN_ENDPOINT,
            data={"grant_type": "client_credentials"},
            auth=httpx.BasicAuth(self._client_id, self._secret_id),
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

    def list_products(self) -> list[dict[str, Any]]:
        response = self._request("GET", PRODUCT_ENDPOINT)
        return response.json()

    def get_product(self, external_id: str) -> dict[str, Any]:
        response = self._request("GET", f"{PRODUCT_ENDPOINT}/{external_id}")
        return response.json()

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request("POST", PRODUCT_ENDPOINT, json=payload)
        return response.json()

    def update_product(self, external_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request("PATCH", f"{PRODUCT_ENDPOINT}/{external_id}", json=payload)
        return response.json()

    def delete_product(self, external_id: str) -> None:
        self._request("DELETE", f"{PRODUCT_ENDPOINT}/{external_id}")

    def list_unit_measures(self) -> list[dict[str, Any]]:
        response = self._request("GET", UNIT_MEASURE_ENDPOINT)
        return response.json()

    def get_unit_measure(self, external_id: str) -> dict[str, Any]:
        response = self._request("GET", f"{UNIT_MEASURE_ENDPOINT}/{external_id}")
        return response.json()

    def create_unit_measure(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request("POST", UNIT_MEASURE_ENDPOINT, json=payload)
        return response.json()

    def update_unit_measure(self, external_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request("PATCH", f"{UNIT_MEASURE_ENDPOINT}/{external_id}", json=payload)
        return response.json()

    def delete_unit_measure(self, external_id: str) -> None:
        self._request("DELETE", f"{UNIT_MEASURE_ENDPOINT}/{external_id}")
