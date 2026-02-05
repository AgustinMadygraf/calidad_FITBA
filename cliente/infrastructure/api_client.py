"""
Path: cliente/infrastructure/api_client.py
"""

import os
import httpx
from cliente.dtos.res_partner_dto import ResPartnerDTO
from cliente.dtos.stock_picking_dto import StockPickingDTO
from cliente.dtos.stock_package_type_dto import StockPackageTypeDTO
from cliente.dtos.stock_quant_package_dto import StockQuantPackageDTO

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

    def create_res_partner(self, payload: dict) -> ResPartnerDTO:
        r = self._request("post", "/api/v1/res-partners", json=payload)
        return self._handle_res_partner(r)

    def update_res_partner(self, partner_id: int, payload: dict) -> ResPartnerDTO:
        r = self._request("put", f"/api/v1/res-partners/{partner_id}", json=payload)
        return self._handle_res_partner(r)

    def delete_res_partner(self, partner_id: int) -> None:
        r = self._request("delete", f"/api/v1/res-partners/{partner_id}")
        if r.status_code != 204:
            self._raise(r)

    def get_res_partner(self, partner_id: int) -> ResPartnerDTO:
        r = self._request("get", f"/api/v1/res-partners/{partner_id}")
        return self._handle_res_partner(r)

    def list_res_partners(self, limit: int = 10, offset: int = 0) -> list[ResPartnerDTO]:
        r = self._request("get", "/api/v1/res-partners", params={"limit": limit, "offset": offset})
        if r.status_code != 200:
            self._raise(r)
        return [ResPartnerDTO(**item) for item in r.json()["items"]]

    def create_stock_picking(self, payload: dict) -> StockPickingDTO:
        r = self._request("post", "/api/v1/stock-pickings", json=payload)
        return self._handle_stock_picking(r)

    def update_stock_picking(self, picking_id: int, payload: dict) -> StockPickingDTO:
        r = self._request("put", f"/api/v1/stock-pickings/{picking_id}", json=payload)
        return self._handle_stock_picking(r)

    def delete_stock_picking(self, picking_id: int) -> None:
        r = self._request("delete", f"/api/v1/stock-pickings/{picking_id}")
        if r.status_code != 204:
            self._raise(r)

    def get_stock_picking(self, picking_id: int) -> StockPickingDTO:
        r = self._request("get", f"/api/v1/stock-pickings/{picking_id}")
        return self._handle_stock_picking(r)

    def list_stock_pickings(self, limit: int = 10, offset: int = 0) -> list[StockPickingDTO]:
        r = self._request("get", "/api/v1/stock-pickings", params={"limit": limit, "offset": offset})
        if r.status_code != 200:
            self._raise(r)
        return [StockPickingDTO(**item) for item in r.json()["items"]]

    def create_stock_package_type(self, payload: dict) -> StockPackageTypeDTO:
        r = self._request("post", "/api/v1/stock-package-types", json=payload)
        return self._handle_stock_package_type(r)

    def update_stock_package_type(self, package_type_id: int, payload: dict) -> StockPackageTypeDTO:
        r = self._request("put", f"/api/v1/stock-package-types/{package_type_id}", json=payload)
        return self._handle_stock_package_type(r)

    def delete_stock_package_type(self, package_type_id: int) -> None:
        r = self._request("delete", f"/api/v1/stock-package-types/{package_type_id}")
        if r.status_code != 204:
            self._raise(r)

    def get_stock_package_type(self, package_type_id: int) -> StockPackageTypeDTO:
        r = self._request("get", f"/api/v1/stock-package-types/{package_type_id}")
        return self._handle_stock_package_type(r)

    def list_stock_package_types(self, limit: int = 10, offset: int = 0) -> list[StockPackageTypeDTO]:
        r = self._request("get", "/api/v1/stock-package-types", params={"limit": limit, "offset": offset})
        if r.status_code != 200:
            self._raise(r)
        return [StockPackageTypeDTO(**item) for item in r.json()["items"]]

    def create_stock_quant_package(self, payload: dict) -> StockQuantPackageDTO:
        r = self._request("post", "/api/v1/stock-quant-packages", json=payload)
        return self._handle_stock_quant_package(r)

    def update_stock_quant_package(self, package_id: int, payload: dict) -> StockQuantPackageDTO:
        r = self._request("put", f"/api/v1/stock-quant-packages/{package_id}", json=payload)
        return self._handle_stock_quant_package(r)

    def delete_stock_quant_package(self, package_id: int) -> None:
        r = self._request("delete", f"/api/v1/stock-quant-packages/{package_id}")
        if r.status_code != 204:
            self._raise(r)

    def get_stock_quant_package(self, package_id: int) -> StockQuantPackageDTO:
        r = self._request("get", f"/api/v1/stock-quant-packages/{package_id}")
        return self._handle_stock_quant_package(r)

    def list_stock_quant_packages(self, limit: int = 10, offset: int = 0) -> list[StockQuantPackageDTO]:
        r = self._request("get", "/api/v1/stock-quant-packages", params={"limit": limit, "offset": offset})
        if r.status_code != 200:
            self._raise(r)
        return [StockQuantPackageDTO(**item) for item in r.json()["items"]]

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            return self._client.request(method, url, **kwargs)
        except httpx.ConnectError as exc:
            raise ApiError(0, f"No se pudo conectar a la API ({self.base_url})") from exc
        except httpx.RequestError as exc:
            raise ApiError(0, "Error de red al conectar con la API") from exc

    def _handle_res_partner(self, r: httpx.Response) -> ResPartnerDTO:
        if r.status_code not in (200, 201):
            self._raise(r)
        return ResPartnerDTO(**r.json())

    def _handle_stock_picking(self, r: httpx.Response) -> StockPickingDTO:
        if r.status_code not in (200, 201):
            self._raise(r)
        return StockPickingDTO(**r.json())

    def _handle_stock_package_type(self, r: httpx.Response) -> StockPackageTypeDTO:
        if r.status_code not in (200, 201):
            self._raise(r)
        return StockPackageTypeDTO(**r.json())

    def _handle_stock_quant_package(self, r: httpx.Response) -> StockQuantPackageDTO:
        if r.status_code not in (200, 201):
            self._raise(r)
        return StockQuantPackageDTO(**r.json())

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
