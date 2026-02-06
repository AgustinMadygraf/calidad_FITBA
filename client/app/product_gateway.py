from __future__ import annotations

from typing import Any, Protocol

from .real_xubio_client import RealXubioClient


class ProductGateway(Protocol):
    title: str

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
    external_id = item.get("productoid") or item.get("productoId") or item.get("id") or item.get("external_id")
    name = item.get("nombre") or item.get("name") or item.get("descripcion") or "SIN_NOMBRE"
    sku = item.get("codigo") or item.get("sku") or "-"
    price = item.get("precioVenta") or item.get("price") or "-"
    return "\n".join(
        [
            "Producto:",
            f"ID: {external_id}",
            f"Nombre: {name}",
            f"SKU: {sku}",
            f"Precio: {price}",
        ]
    )


class LocalFastApiProductGateway:
    title = "PRODUCTO (LOCAL)"

    def __init__(self, post_execute) -> None:
        self._post_execute = post_execute

    def render_menu(self, session_id: str) -> str:
        return self._post_execute(session_id, "ENTER product")["screen"]

    def create(
        self,
        *,
        session_id: str,
        external_id: str | None,
        name: str,
        sku: str | None,
        price: float | None,
    ) -> str:
        args = {"external_id": external_id, "name": name, "sku": sku, "price": price}
        return self._post_execute(session_id, "CREATE product", args)["screen"]

    def update(
        self,
        *,
        session_id: str,
        external_id: str,
        name: str | None,
        sku: str | None,
        price: float | None,
    ) -> str:
        args = {"external_id": external_id, "name": name, "sku": sku, "price": price}
        return self._post_execute(session_id, "UPDATE product", args)["screen"]

    def delete(self, *, session_id: str, external_id: str) -> str:
        return self._post_execute(session_id, "DELETE product", {"external_id": external_id})["screen"]

    def get(self, *, session_id: str, external_id: str) -> str:
        return self._post_execute(session_id, "GET product", {"external_id": external_id})["screen"]

    def list(self, *, session_id: str) -> str:
        return self._post_execute(session_id, "LIST product", {})["screen"]

    def sync_pull(self, *, session_id: str) -> str:
        return self._post_execute(session_id, "SYNC_PULL product", {})["screen"]

    def on_back(self, session_id: str) -> None:
        self._post_execute(session_id, "BACK")


class XubioDirectProductGateway:
    title = "PRODUCTO (XUBIO REAL)"

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
                "6) Sincronizar (bajar)",
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
        lines = ["Productos:"]
        for item in items:
            external_id = item.get("productoid") or item.get("productoId") or item.get("id")
            name = item.get("nombre") or item.get("name") or item.get("descripcion") or "SIN_NOMBRE"
            lines.append(f"- {external_id} | {name}")
        return "\n".join(lines)

    def sync_pull(self, *, session_id: str) -> str:
        _ = session_id
        return "No disponible en modo real desde el cliente."

    def on_back(self, session_id: str) -> None:
        _ = session_id
