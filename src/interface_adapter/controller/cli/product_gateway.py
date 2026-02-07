from __future__ import annotations

from typing import Any, Protocol

from .local_xubio_client import LocalXubioClient
from .real_xubio_client import RealXubioClient
from src.interface_adapter.presenters.product_presenter import (
    extract_product_id,
    extract_product_name,
    format_product_screen,
)


class ProductGateway(Protocol):
    title: str
    show_sync_pull: bool
    back_option: str

    def render_menu(self, session_id: str) -> str:
        ...

    def create(
        self,
        *,
        session_id: str,
        external_id: str | None,
        name: str,
        sku: str | None,
        price: float | None,
    ) -> str:
        ...

    def update(
        self,
        *,
        session_id: str,
        external_id: str,
        name: str | None,
        sku: str | None,
        price: float | None,
    ) -> str:
        ...

    def delete(self, *, session_id: str, external_id: str) -> str:
        ...

    def get(self, *, session_id: str, external_id: str) -> str:
        ...

    def list(self, *, session_id: str) -> str:
        ...

    def sync_pull(self, *, session_id: str) -> str:
        ...

    def on_back(self, session_id: str) -> None:
        ...


def map_product_screen(item: dict[str, Any]) -> str:
    return format_product_screen(item)


class LocalFastApiProductGateway:
    title = "PRODUCTO (LOCAL)"
    show_sync_pull = True
    back_option = "7"

    def __init__(self, base_url: str) -> None:
        self._client = LocalXubioClient(base_url)

    def render_menu(self, session_id: str) -> str:
        _ = session_id
        return "\n".join(
            [
                "1) Alta",
                "2) Modificar",
                "3) Baja",
                "4) Consultar por ID",
                "5) Listar",
                "6) Sincronizar (bajar de Xubio)",
                "7) Volver",
            ]
        )

    def create(
        self,
        *,
        session_id: str,
        external_id: str | None,
        name: str,
        sku: str | None,
        price: float | None,
    ) -> str:
        _ = session_id
        payload: dict[str, Any] = {"nombre": name, "codigo": sku, "precioVenta": price}
        if external_id:
            payload["productoid"] = external_id
        result = self._client.create_product(payload)
        return map_product_screen(result)

    def update(
        self,
        *,
        session_id: str,
        external_id: str,
        name: str | None,
        sku: str | None,
        price: float | None,
    ) -> str:
        _ = session_id
        payload = {"nombre": name, "codigo": sku, "precioVenta": price}
        result = self._client.update_product(external_id, payload)
        return map_product_screen(result)

    def delete(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        self._client.delete_product(external_id)
        return "Producto eliminado."

    def get(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        result = self._client.get_product(external_id)
        return map_product_screen(result)

    def list(self, *, session_id: str) -> str:
        _ = session_id
        items = self._client.list_products()
        if not items:
            return "Sin productos."
        lines = ["Productos:", "ID | Nombre"]
        for item in items:
            external_id = extract_product_id(item)
            name = extract_product_name(item)
            lines.append(f"- {external_id} | {name}")
        return "\n".join(lines)

    def sync_pull(self, *, session_id: str) -> str:
        _ = session_id
        result = self._client.sync_pull_from_xubio()
        if result.get("status") == "ok":
            return "Sync pull OK: datos actualizados desde Xubio."
        detail = result.get("detail", "desconocido")
        return f"Sync pull ERROR: {detail}"

    def on_back(self, session_id: str) -> None:
        _ = session_id


class XubioDirectProductGateway:
    title = "PRODUCTO (XUBIO REAL)"
    show_sync_pull = False
    back_option = "6"

    def __init__(self, client_id: str, secret_id: str):
        self._client = RealXubioClient(client_id, secret_id)

    def render_menu(self, session_id: str) -> str:
        _ = session_id
        return "\n".join(
            [
                "1) Alta",
                "2) Modificar",
                "3) Baja",
                "4) Consultar por ID",
                "5) Listar",
                "6) Volver",
            ]
        )

    def create(
        self,
        *,
        session_id: str,
        external_id: str | None,
        name: str,
        sku: str | None,
        price: float | None,
    ) -> str:
        _ = session_id
        payload: dict[str, Any] = {"nombre": name, "codigo": sku, "precioVenta": price}
        if external_id:
            payload["productoid"] = external_id
        result = self._client.create_product(payload)
        return map_product_screen(result)

    def update(
        self,
        *,
        session_id: str,
        external_id: str,
        name: str | None,
        sku: str | None,
        price: float | None,
    ) -> str:
        _ = session_id
        payload = {"nombre": name, "codigo": sku, "precioVenta": price}
        result = self._client.update_product(external_id, payload)
        return map_product_screen(result)

    def delete(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        self._client.delete_product(external_id)
        return "Producto eliminado."

    def get(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        result = self._client.get_product(external_id)
        return map_product_screen(result)

    def list(self, *, session_id: str) -> str:
        _ = session_id
        items = self._client.list_products()
        if not items:
            return "Sin productos."
        lines = ["Productos:", "ID | Nombre"]
        for item in items:
            external_id = extract_product_id(item)
            name = extract_product_name(item)
            lines.append(f"- {external_id} | {name}")
        return "\n".join(lines)

    def sync_pull(self, *, session_id: str) -> str:
        _ = session_id
        return "No disponible en modo real desde el cliente."

    def on_back(self, session_id: str) -> None:
        _ = session_id
