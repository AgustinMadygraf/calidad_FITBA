from __future__ import annotations

import shutil
import sys
import uuid
from typing import Any, Callable

import httpx
import typer

from client.app.product_gateway import (
    LocalFastApiProductGateway,
    ProductGateway,
    XubioDirectProductGateway,
)
from client.app.settings import settings

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


def _main_menu_body() -> str:
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


def _build_product_gateway() -> ProductGateway:
    if settings.IS_PROD:
        if not settings.xubio_client_id or not settings.xubio_secret_id:
            raise ValueError("Faltan XUBIO_CLIENT_ID / XUBIO_SECRET_ID")
        return XubioDirectProductGateway(settings.xubio_client_id, settings.xubio_secret_id)
    return LocalFastApiProductGateway(_post_execute)


def _run_action(action_name: str, func: Callable[[], str]) -> str | None:
    try:
        return func()
    except Exception as exc:
        _render_screen("ERROR", f"{action_name}: {exc}", "ENTER para continuar")
        _pause()
        return None


def _product_menu(session_id: str, gateway: ProductGateway) -> None:
    while True:
        try:
            _clear()
            _render_screen(gateway.title, gateway.render_menu(session_id))
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
                screen = _run_action(
                    "Alta producto",
                    lambda: gateway.create(
                        session_id=session_id,
                        external_id=external_id,
                        name=name,
                        sku=sku,
                        price=price,
                    ),
                )
                if screen is not None:
                    _render_screen("RESULTADO", screen, "ENTER para continuar")
                    _pause()
            elif choice == "2":
                external_id = _field_prompt("ID", required=True)
                if external_id is None:
                    continue
                name = _field_prompt("Nombre", required=False)
                sku = _field_prompt("SKU", required=False)
                price = _read_price()
                screen = _run_action(
                    "Modificar producto",
                    lambda: gateway.update(
                        session_id=session_id,
                        external_id=external_id,
                        name=name,
                        sku=sku,
                        price=price,
                    ),
                )
                if screen is not None:
                    _render_screen("RESULTADO", screen, "ENTER para continuar")
                    _pause()
            elif choice == "3":
                external_id = _field_prompt("ID", required=True)
                if external_id is None:
                    continue
                if settings.IS_PROD and not _double_confirm():
                    print("Baja cancelada.")
                    continue
                screen = _run_action(
                    "Baja producto",
                    lambda: gateway.delete(session_id=session_id, external_id=external_id),
                )
                if screen is not None:
                    _render_screen("RESULTADO", screen, "ENTER para continuar")
                    _pause()
            elif choice == "4":
                external_id = _field_prompt("ID", required=True)
                if external_id is None:
                    continue
                screen = _run_action(
                    "Consultar producto",
                    lambda: gateway.get(session_id=session_id, external_id=external_id),
                )
                if screen is not None:
                    _render_screen("RESULTADO", screen, "ENTER para continuar")
                    _pause()
            elif choice == "5":
                screen = _run_action("Listar productos", lambda: gateway.list(session_id=session_id))
                if screen is not None:
                    _render_screen("LISTADO", screen, "ENTER para continuar")
                    _pause()
            elif choice == "6":
                screen = _run_action("Sync pull", lambda: gateway.sync_pull(session_id=session_id))
                if screen is not None:
                    _render_screen("SYNC", screen, "ENTER para continuar")
                    _pause()
            elif choice == "7":
                gateway.on_back(session_id)
                return
            else:
                _render_screen("ERROR", "Opcion invalida.", "ENTER para continuar")
                _pause()
        except Exception as exc:
            _render_screen("ERROR", f"Fallo inesperado: {exc}", "ENTER para continuar")
            _pause()


def _stub_screen(session_id: str, entity_type: str) -> None:
    if settings.IS_PROD:
        _render_screen("INFO", "No implementado aun.", "ENTER para continuar")
        _pause()
        return
    resp = _post_execute(session_id, f"ENTER {entity_type}")
    _render_screen("INFO", resp["screen"], "ENTER para continuar")
    _pause()


@app.command()
def run() -> None:
    session_id = str(uuid.uuid4())
    gateway = _build_product_gateway()
    while True:
        try:
            _clear()
            if settings.IS_PROD:
                menu_screen = _main_menu_body()
            else:
                menu_screen = _post_execute(session_id, "MENU")["screen"]
            mode_label = "PROD" if settings.IS_PROD else "DEV"
            _render_screen(f"TERMINAL FITBA/XUBIO [{mode_label}]", menu_screen)
            choice = _prompt("> ")
            if choice == "1":
                _product_menu(session_id, gateway)
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
