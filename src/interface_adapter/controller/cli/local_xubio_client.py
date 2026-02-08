from __future__ import annotations

from typing import Any

import httpx


class LocalXubioClient:
    def __init__(self, base_url: str) -> None:
        root_base = base_url.rstrip("/")
        api_base = f"{base_url.rstrip('/')}/API/1.1"
        self._client = httpx.Client(base_url=api_base, timeout=20)
        self._sync_client = httpx.Client(base_url=root_base, timeout=20)
        self._root_base = root_base
        self._product_endpoint = "/ProductoVentaBean"
        self._unit_measure_endpoint = "/UnidadMedidaBean"

    def _request(self, client: httpx.Client, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"No se pudo conectar al servidor local ({self._root_base}). "
                "Levanta FastAPI y verifica BASE_URL."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = ""
            try:
                payload = exc.response.json()
                if isinstance(payload, dict) and payload.get("detail"):
                    detail = f": {payload['detail']}"
            except ValueError:
                detail = ""
            raise RuntimeError(f"Servidor local respondio HTTP {exc.response.status_code}{detail}.") from exc

    def list_products(self) -> list[dict[str, Any]]:
        response = self._request(self._client, "GET", self._product_endpoint)
        return response.json()

    def get_product(self, external_id: str) -> dict[str, Any]:
        response = self._request(self._client, "GET", f"{self._product_endpoint}/{external_id}")
        return response.json()

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request(self._client, "POST", self._product_endpoint, json=payload)
        return response.json()

    def update_product(self, external_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request(
            self._client,
            "PATCH",
            f"{self._product_endpoint}/{external_id}",
            json=payload,
        )
        return response.json()

    def delete_product(self, external_id: str) -> None:
        self._request(self._client, "DELETE", f"{self._product_endpoint}/{external_id}")

    def sync_pull_from_xubio(self) -> dict[str, Any]:
        response = self._request(self._sync_client, "POST", "/sync/pull/product/from-xubio")
        return response.json()

    def sync_pull_unit_measure_from_xubio(self) -> dict[str, Any]:
        response = self._request(self._sync_client, "POST", "/sync/pull/unit-measure/from-xubio")
        return response.json()

    def list_unit_measures(self) -> list[dict[str, Any]]:
        response = self._request(self._client, "GET", self._unit_measure_endpoint)
        return response.json()

    def get_unit_measure(self, external_id: str) -> dict[str, Any]:
        response = self._request(self._client, "GET", f"{self._unit_measure_endpoint}/{external_id}")
        return response.json()

    def create_unit_measure(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request(self._client, "POST", self._unit_measure_endpoint, json=payload)
        return response.json()

    def update_unit_measure(self, external_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._request(
            self._client,
            "PATCH",
            f"{self._unit_measure_endpoint}/{external_id}",
            json=payload,
        )
        return response.json()

    def delete_unit_measure(self, external_id: str) -> None:
        self._request(self._client, "DELETE", f"{self._unit_measure_endpoint}/{external_id}")
