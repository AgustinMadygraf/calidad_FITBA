from __future__ import annotations

import sys
import uuid
from typing import Any
import shutil

import httpx
import typer

from client.app.settings import settings
from .real_xubio_client import RealXubioClient

app = typer.Typer(add_completion=False)


def _post_execute(session_id: str, command: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "session_id": session_id,
        "command": command,
        "args": args or {},
    }
    try:
        response = httpx.post(f"{settings.base_url}/terminal/execute", json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as exc:
        return {
            "session_id": session_id,
            "screen": f"Error de conexion: {exc.__class__.__name__}. Verifique BASE_URL.",
            "next_actions": [],
        }
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        return {
            "session_id": session_id,
            "screen": f"Error HTTP {status}. Intente nuevamente.",
            "next_actions": [],
        }
    except ValueError:
        return {
            "session_id": session_id,
            "screen": "Respuesta invalida del servidor.",
            "next_actions": [],
        }


def _prompt(text: str) -> str:
    try:
        return input(text).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nSaliendo...")
        sys.exit(0)


def _double_confirm() -> bool:
    first = _prompt("Confirmar BAJA (escriba SI): ")
    if first.upper() != "SI":
        return False
    second = _prompt("Confirmar nuevamente (escriba SI): ")
    return second.upper() == "SI"


def _clear() -> None:
    print("\033c", end="")


def _term_width(min_width: int = 60) -> int:
    return max(shutil.get_terminal_size(fallback=(min_width, 24)).columns, min_width)


def _apply_theme(text: str) -> str:
    # Black background, green foreground
    return f"\033[32;40m{text}\033[0m"


def _render_screen(title: str, body: str, footer: str = "") -> None:
    lines = body.splitlines() if body else [""]
    width = min(
        max(len(title) + 4, *(len(line) for line in lines), len(footer), 40),
        _term_width() - 4,
    )
    top = "+" + "-" * (width + 2) + "+"
    print(_apply_theme(top))
    print(_apply_theme(f"| {title.center(width)} |"))
    print(_apply_theme("+" + "-" * (width + 2) + "+"))
    for line in lines:
        print(_apply_theme(f"| {line.ljust(width)} |"))
    if footer:
        print(_apply_theme("+" + "-" * (width + 2) + "+"))
        print(_apply_theme(f"| {footer.ljust(width)} |"))
    print(_apply_theme(top))


def _pause() -> None:
    _prompt("ENTER para continuar...")


def _field_prompt(label: str, *, required: bool = False, default: str | None = None) -> str | None:
    suffix = " (obligatorio)" if required else ""
    default_txt = f" [{default}]" if default else ""
    padded_label = label.ljust(12)
    value = _prompt(f"{padded_label}{suffix}{default_txt}: ")
    if not value and default is not None:
        return default
    if required and not value:
        _render_screen("ERROR", f"El campo '{label}' es obligatorio.", "ENTER para continuar")
        _pause()
        return None
    return value or None


def _read_price() -> float | None:
    raw = _prompt(f"{'Precio'.ljust(12)} (opcional): ")
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        _render_screen("ERROR", "Precio invalido.", "ENTER para continuar")
        _pause()
        return None


def _get_real_client() -> RealXubioClient:
    if not settings.xubio_client_id or not settings.xubio_secret_id:
        raise ValueError("Faltan XUBIO_CLIENT_ID / XUBIO_SECRET_ID")
    return RealXubioClient(settings.xubio_client_id, settings.xubio_secret_id)


def _run_real(action_name: str, func) -> Any | None:
    try:
        return func()
    except Exception as exc:
        _render_screen("ERROR", f"{action_name}: {exc}", "ENTER para continuar")
        _pause()
        return None


def _map_product_screen(item: dict[str, Any]) -> str:
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


def _render_product_menu_real() -> None:
    body = "\n".join(
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
    _render_screen("PRODUCTO (XUBIO REAL)", body)


def _render_product_menu_mock(session_id: str) -> None:
    resp = _post_execute(session_id, "ENTER product")
    _render_screen("PRODUCTO (LOCAL)", resp["screen"])


def _product_menu(session_id: str) -> None:
    while True:
        try:
            _clear()
            if settings.is_xubio_mode_mock:
                _render_product_menu_mock(session_id)
            else:
                _render_product_menu_real()
            choice = _prompt("> ")
            if choice == "1":
                external_id = _field_prompt("ID", required=False)
                name = _field_prompt("Nombre", required=True)
                if name is None:
                    continue
                sku = _field_prompt("SKU", required=False)
                price = _read_price()
                if price is None and _prompt("Continuar sin precio? (S/N): ").upper() not in {"S", "SI"}:
                    continue
                if settings.is_xubio_mode_mock:
                    args = {"external_id": external_id, "name": name, "sku": sku, "price": price}
                    resp = _post_execute(session_id, "CREATE product", args)
                    _render_screen("RESULTADO", resp["screen"], "ENTER para continuar")
                    _pause()
                else:
                    def _action():
                        client = _get_real_client()
                        payload = {"nombre": name, "codigo": sku, "precioVenta": price}
                        if external_id:
                            payload["productoid"] = external_id
                        return client.create_product(payload)

                    result = _run_real("Alta producto", _action)
                    if result is not None:
                        _render_screen("RESULTADO", _map_product_screen(result), "ENTER para continuar")
                        _pause()
            elif choice == "2":
                external_id = _field_prompt("ID", required=True)
                if external_id is None:
                    continue
                name = _field_prompt("Nombre", required=False)
                sku = _field_prompt("SKU", required=False)
                price = _read_price()
                if settings.is_xubio_mode_mock:
                    args = {"external_id": external_id, "name": name, "sku": sku, "price": price}
                    resp = _post_execute(session_id, "UPDATE product", args)
                    _render_screen("RESULTADO", resp["screen"], "ENTER para continuar")
                    _pause()
                else:
                    def _action():
                        client = _get_real_client()
                        payload = {"nombre": name, "codigo": sku, "precioVenta": price}
                        return client.update_product(external_id, payload)

                    result = _run_real("Modificar producto", _action)
                    if result is not None:
                        _render_screen("RESULTADO", _map_product_screen(result), "ENTER para continuar")
                        _pause()
            elif choice == "3":
                external_id = _field_prompt("ID", required=True)
                if external_id is None:
                    continue
                if not settings.is_xubio_mode_mock and not _double_confirm():
                    print("Baja cancelada.")
                    continue
                if settings.is_xubio_mode_mock:
                    resp = _post_execute(session_id, "DELETE product", {"external_id": external_id})
                    _render_screen("RESULTADO", resp["screen"], "ENTER para continuar")
                    _pause()
                else:
                    def _action():
                        client = _get_real_client()
                        client.delete_product(external_id)
                        return True

                    if _run_real("Baja producto", _action):
                        _render_screen("RESULTADO", "Producto eliminado.", "ENTER para continuar")
                        _pause()
            elif choice == "4":
                external_id = _field_prompt("ID", required=True)
                if external_id is None:
                    continue
                if settings.is_xubio_mode_mock:
                    resp = _post_execute(session_id, "GET product", {"external_id": external_id})
                    _render_screen("RESULTADO", resp["screen"], "ENTER para continuar")
                    _pause()
                else:
                    def _action():
                        client = _get_real_client()
                        return client.get_product(external_id)

                    result = _run_real("Consultar producto", _action)
                    if result is not None:
                        _render_screen("RESULTADO", _map_product_screen(result), "ENTER para continuar")
                        _pause()
            elif choice == "5":
                if settings.is_xubio_mode_mock:
                    resp = _post_execute(session_id, "LIST product", {})
                    _render_screen("LISTADO", resp["screen"], "ENTER para continuar")
                    _pause()
                else:
                    def _action():
                        client = _get_real_client()
                        return client.list_products()

                    items = _run_real("Listar productos", _action)
                    if items is None:
                        continue
                    if not items:
                        _render_screen("LISTADO", "Sin productos.", "ENTER para continuar")
                        _pause()
                    else:
                        lines = ["Productos:"]
                        for item in items:
                            external_id = item.get("productoid") or item.get("productoId") or item.get("id")
                            name = item.get("nombre") or item.get("name") or item.get("descripcion") or "SIN_NOMBRE"
                            lines.append(f"- {external_id} | {name}")
                        _render_screen("LISTADO", "\n".join(lines), "ENTER para continuar")
                        _pause()
            elif choice == "6":
                if settings.is_xubio_mode_mock:
                    resp = _post_execute(session_id, "SYNC_PULL product", {})
                    _render_screen("SYNC", resp["screen"], "ENTER para continuar")
                    _pause()
                    continue
                _render_screen("SYNC", "No disponible en modo real desde el cliente.", "ENTER para continuar")
                _pause()
                continue
            elif choice == "7":
                if settings.is_xubio_mode_mock:
                    _post_execute(session_id, "BACK")
                return
            else:
                _render_screen("ERROR", "Opcion invalida.", "ENTER para continuar")
                _pause()
        except Exception as exc:
            _render_screen("ERROR", f"Fallo inesperado: {exc}", "ENTER para continuar")
            _pause()


def _stub_screen(session_id: str, entity_type: str) -> None:
    if settings.is_xubio_mode_mock:
        resp = _post_execute(session_id, f"ENTER {entity_type}")
        _render_screen("INFO", resp["screen"], "ENTER para continuar")
        _pause()
    else:
        _render_screen("INFO", "No implementado aun.", "ENTER para continuar")
        _pause()


@app.command()
def run() -> None:
    session_id = str(uuid.uuid4())
    while True:
        try:
            _clear()
            resp = _post_execute(session_id, "MENU")
            mode_label = "DEV" if settings.is_xubio_mode_mock else "PROD"
            _render_screen(f"TERMINAL FITBA/XUBIO [{mode_label}]", resp["screen"])
            choice = _prompt("> ")
            if choice == "1":
                _product_menu(session_id)
            elif choice == "2":
                _stub_screen(session_id, "client")
            elif choice == "3":
                _stub_screen(session_id, "supplier")
            elif choice == "4":
                _stub_screen(session_id, "invoice")
            elif choice == "5":
                _stub_screen(session_id, "scale")
            elif choice.lower() in {"q", "quit", "salir"}:
                sys.exit(0)
            else:
                _render_screen("ERROR", "Opcion invalida.", "ENTER para continuar")
                _pause()
        except Exception as exc:
            _render_screen("ERROR", f"Fallo inesperado: {exc}", "ENTER para continuar")
            _pause()


if __name__ == "__main__":
    run()
