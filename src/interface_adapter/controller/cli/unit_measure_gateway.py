from __future__ import annotations

from typing import Any, Protocol

from .local_xubio_client import LocalXubioClient
from .real_xubio_client import RealXubioClient


class UnitMeasureGateway(Protocol):
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
        code: str | None,
        name: str | None,
    ) -> str:
        ...

    def update(
        self,
        *,
        session_id: str,
        external_id: str,
        code: str | None,
        name: str | None,
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


def _extract_unit_measure_id(item: dict[str, Any]) -> str | None:
    value = item.get("ID") or item.get("id") or item.get("external_id")
    return str(value) if value is not None else None


def _extract_unit_measure_code(item: dict[str, Any]) -> str:
    return str(item.get("codigo") or item.get("code") or "-")


def _extract_unit_measure_name(item: dict[str, Any]) -> str:
    name = item.get("nombre") or item.get("name") or "SIN_NOMBRE"
    return " ".join(str(name).split())


def _format_unit_measure_screen(item: dict[str, Any]) -> str:
    external_id = _extract_unit_measure_id(item)
    code = _extract_unit_measure_code(item)
    name = _extract_unit_measure_name(item)
    return "\n".join(
        [
            "Unidad de medida:",
            f"ID: {external_id}",
            f"Codigo: {code}",
            f"Nombre: {name}",
        ]
    )


class LocalFastApiUnitMeasureGateway:
    title = "UNIDAD MEDIDA (LOCAL)"
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
        code: str | None,
        name: str | None,
    ) -> str:
        _ = session_id
        payload: dict[str, Any] = {"codigo": code, "nombre": name}
        if external_id:
            payload["ID"] = external_id
        result = self._client.create_unit_measure(payload)
        return _format_unit_measure_screen(result)

    def update(
        self,
        *,
        session_id: str,
        external_id: str,
        code: str | None,
        name: str | None,
    ) -> str:
        _ = session_id
        payload = {"codigo": code, "nombre": name}
        result = self._client.update_unit_measure(external_id, payload)
        return _format_unit_measure_screen(result)

    def delete(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        self._client.delete_unit_measure(external_id)
        return "Unidad de medida eliminada."

    def get(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        result = self._client.get_unit_measure(external_id)
        return _format_unit_measure_screen(result)

    def list(self, *, session_id: str) -> str:
        _ = session_id
        items = self._client.list_unit_measures()
        if not items:
            return "Sin unidades de medida."
        lines = ["Unidades de medida:", "ID | Codigo | Nombre"]
        for item in items:
            external_id = _extract_unit_measure_id(item)
            code = _extract_unit_measure_code(item)
            name = _extract_unit_measure_name(item)
            lines.append(f"- {external_id} | {code} | {name}")
        return "\n".join(lines)

    def sync_pull(self, *, session_id: str) -> str:
        _ = session_id
        result = self._client.sync_pull_unit_measure_from_xubio()
        if result.get("status") == "ok":
            return "Sync pull OK: datos actualizados desde Xubio."
        detail = result.get("detail", "desconocido")
        return f"Sync pull ERROR: {detail}"

    def on_back(self, session_id: str) -> None:
        _ = session_id


class XubioDirectUnitMeasureGateway:
    title = "UNIDAD MEDIDA (XUBIO REAL)"
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
        code: str | None,
        name: str | None,
    ) -> str:
        _ = session_id
        payload: dict[str, Any] = {"codigo": code, "nombre": name}
        if external_id:
            payload["ID"] = external_id
        result = self._client.create_unit_measure(payload)
        return _format_unit_measure_screen(result)

    def update(
        self,
        *,
        session_id: str,
        external_id: str,
        code: str | None,
        name: str | None,
    ) -> str:
        _ = session_id
        payload = {"codigo": code, "nombre": name}
        result = self._client.update_unit_measure(external_id, payload)
        return _format_unit_measure_screen(result)

    def delete(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        self._client.delete_unit_measure(external_id)
        return "Unidad de medida eliminada."

    def get(self, *, session_id: str, external_id: str) -> str:
        _ = session_id
        result = self._client.get_unit_measure(external_id)
        return _format_unit_measure_screen(result)

    def list(self, *, session_id: str) -> str:
        _ = session_id
        items = self._client.list_unit_measures()
        if not items:
            return "Sin unidades de medida."
        lines = ["Unidades de medida:", "ID | Codigo | Nombre"]
        for item in items:
            external_id = _extract_unit_measure_id(item)
            code = _extract_unit_measure_code(item)
            name = _extract_unit_measure_name(item)
            lines.append(f"- {external_id} | {code} | {name}")
        return "\n".join(lines)

    def sync_pull(self, *, session_id: str) -> str:
        _ = session_id
        return "No disponible en modo real desde el cliente."

    def on_back(self, session_id: str) -> None:
        _ = session_id
