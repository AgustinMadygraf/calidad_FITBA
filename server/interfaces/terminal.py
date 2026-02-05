from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shared.schemas import ProductCreate, ProductUpdate
from server.application.use_cases import (
    CreateProduct,
    DeleteProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
)
from server.infrastructure.clients.xubio_api_client import XubioApiClient
from server.app.settings import settings


@dataclass
class TerminalSession:
    current_entity: str | None = None


SESSIONS: dict[str, TerminalSession] = {}


def _render_main_menu() -> str:
    return "\n".join(
        [
            "=== TERMINAL FITBA/XUBIO ===",
            "",
            "1) PRODUCTO",
            "2) CLIENTE (stub)",
            "3) PROVEEDOR (stub)",
            "4) COMPROBANTES (stub)",
            "5) PESADAS (stub)",
            "",
            "Seleccione una opcion.",
        ]
    )


def _render_entity_menu(entity_type: str) -> str:
    return "\n".join(
        [
            f"=== {entity_type.upper()} ===",
            "",
            "1) Alta",
            "2) Modificar",
            "3) Baja",
            "4) Consultar por ID",
            "5) Listar",
            "6) Volver",
        ]
    )


def _render_stub() -> str:
    return "No implementado aun.\nPresione ENTER para volver."


def execute_command(
    *,
    session_id: str,
    command: str,
    args: dict[str, Any],
    client: XubioApiClient,
) -> tuple[str, str, list[str]]:
    session = SESSIONS.setdefault(session_id, TerminalSession())
    tokens = command.strip().split()
    if not tokens:
        return session_id, _render_main_menu(), ["MENU"]

    verb = tokens[0].upper()
    if verb == "MENU":
        session.current_entity = None
        return session_id, _render_main_menu(), ["ENTER product", "ENTER client", "ENTER supplier"]

    if verb == "BACK":
        session.current_entity = None
        return session_id, _render_main_menu(), ["MENU"]

    if verb == "ENTER":
        entity_type = (tokens[1] if len(tokens) > 1 else args.get("entity_type", "")).lower()
        session.current_entity = entity_type
        if entity_type == "product":
            return session_id, _render_entity_menu(entity_type), []
        return session_id, _render_stub(), []

    if verb in {"CREATE", "UPDATE", "DELETE", "GET", "LIST"}:
        entity_type = (tokens[1] if len(tokens) > 1 else args.get("entity_type", "")).lower()
        if entity_type != "product":
            return session_id, _render_stub(), []

        if verb == "CREATE":
            payload = ProductCreate(**args)
            dto = CreateProduct(client).execute(payload)
            screen = f"Producto creado/actualizado.\nID: {dto.external_id}\nNombre: {dto.name}"
            return session_id, screen, []

        if verb == "UPDATE":
            external_id = args.get("external_id")
            if not external_id:
                return session_id, "Falta external_id.", []
            payload = ProductUpdate(**args)
            dto = UpdateProduct(client).execute(external_id, payload)
            screen = f"Producto actualizado.\nID: {dto.external_id}\nNombre: {dto.name}"
            return session_id, screen, []

        if verb == "DELETE":
            external_id = args.get("external_id")
            if not external_id:
                return session_id, "Falta external_id.", []
            if settings.xubio_mode == "real" and settings.disable_delete_in_real:
                return session_id, "Baja deshabilitada por configuracion.", []
            DeleteProduct(client).execute(external_id)
            return session_id, "Producto eliminado.", []

        if verb == "GET":
            external_id = args.get("external_id")
            if not external_id:
                return session_id, "Falta external_id.", []
            dto = GetProduct(client).execute(external_id)
            screen = "\n".join(
                [
                    "Producto:",
                    f"ID: {dto.external_id}",
                    f"Nombre: {dto.name}",
                    f"SKU: {dto.sku or '-'}",
                    f"Precio: {dto.price if dto.price is not None else '-'}",
                ]
            )
            return session_id, screen, []

        if verb == "LIST":
            limit = int(args.get("limit", 50))
            offset = int(args.get("offset", 0))
            items = ListProducts(client).execute(limit=limit, offset=offset)
            if not items:
                return session_id, "Sin productos.", []
            lines = ["Productos:"]
            for item in items:
                lines.append(f"- {item.external_id} | {item.name}")
            return session_id, "\n".join(lines), []

    return session_id, "Comando desconocido.", []
