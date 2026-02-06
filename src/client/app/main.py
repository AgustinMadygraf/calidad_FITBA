from __future__ import annotations

import shutil
import sys
import uuid
from datetime import datetime
from typing import Callable

import typer

from src.client.app.product_gateway import (
    LocalFastApiProductGateway,
    ProductGateway,
    XubioDirectProductGateway,
)
from src.client.app.settings import settings

app = typer.Typer(add_completion=False)
_CURRENT_SESSION_ID = "-"
_IS_PROD_OVERRIDE: bool | None = None


def _parse_bool_option(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise typer.BadParameter("IS_PROD debe ser booleano (true/false).")


def _is_prod_enabled() -> bool:
    if _IS_PROD_OVERRIDE is not None:
        return _IS_PROD_OVERRIDE
    return settings.IS_PROD


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


def _term_height(min_height: int = 20) -> int:
    return max(shutil.get_terminal_size(fallback=(80, min_height)).lines, min_height)


def _apply_theme(text: str) -> str:
    return f"\033[32;40m{text}\033[0m"


def _status_line() -> str:
    mode = "PROD" if _is_prod_enabled() else "DEV"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"MODO:{mode} | SESION:{_CURRENT_SESSION_ID[:8]} | {now}"


def _fit_text(text: str, width: int) -> str:
    if len(text) <= width:
        return text.ljust(width)
    if width <= 3:
        return text[:width]
    return f"{text[: width - 3]}..."


def _render_screen(title: str, body: str, footer: str = "") -> None:
    lines = body.splitlines() if body else [""]
    status = _status_line()
    width = min(
        max(len(title) + 4, *(len(line) for line in lines), len(footer), len(status), 40),
        _term_width() - 4,
    )
    top = "+" + "-" * (width + 2) + "+"
    print(_apply_theme(top))
    print(_apply_theme(f"| {title.center(width)} |"))
    print(_apply_theme("+" + "-" * (width + 2) + "+"))
    for line in lines:
        print(_apply_theme(f"| {_fit_text(line, width)} |"))
    print(_apply_theme("+" + "-" * (width + 2) + "+"))
    if footer:
        print(_apply_theme(f"| {_fit_text(footer, width)} |"))
        print(_apply_theme("+" + "-" * (width + 2) + "+"))
    print(_apply_theme(f"| {_fit_text(status, width)} |"))
    print(_apply_theme(top))


def _render_paginated_screen(title: str, body: str, footer: str = "ENTER para continuar") -> None:
    lines = body.splitlines() if body else [""]
    lines_per_page = max(5, _term_height() - 10)
    total_pages = (len(lines) + lines_per_page - 1) // lines_per_page
    current_page = 0

    while True:
        start = current_page * lines_per_page
        end = start + lines_per_page
        chunk = lines[start:end]
        page_footer = footer
        if total_pages > 1:
            page_footer = f"ENTER sig. | B ant. | Q salir | Pag {current_page + 1}/{total_pages}"
        _render_screen(title, "\n".join(chunk), page_footer)

        if total_pages == 1:
            _pause()
            return

        cmd = _prompt("> ").strip().lower()
        if cmd in {"q", "quit", "salir"}:
            return
        if cmd == "b":
            current_page = max(0, current_page - 1)
            _clear()
            continue
        if current_page >= total_pages - 1:
            return
        current_page += 1
        _clear()


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
    if _is_prod_enabled():
        if not settings.xubio_client_id or not settings.xubio_secret_id:
            raise ValueError("Faltan XUBIO_CLIENT_ID / XUBIO_SECRET_ID")
        return XubioDirectProductGateway(settings.xubio_client_id, settings.xubio_secret_id)
    return LocalFastApiProductGateway(settings.base_url)


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
                if _is_prod_enabled() and not _double_confirm():
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
                    _render_paginated_screen("LISTADO", screen)
            elif choice == "6" and gateway.show_sync_pull:
                screen = _run_action("Sync pull", lambda: gateway.sync_pull(session_id=session_id))
                if screen is not None:
                    _render_screen("SYNC", screen, "ENTER para continuar")
                    _pause()
            elif choice == gateway.back_option:
                gateway.on_back(session_id)
                return
            else:
                _render_screen("ERROR", "Opcion invalida.", "ENTER para continuar")
                _pause()
        except Exception as exc:
            _render_screen("ERROR", f"Fallo inesperado: {exc}", "ENTER para continuar")
            _pause()


def _stub_screen(session_id: str, entity_type: str) -> None:
    _ = (session_id, entity_type)
    _render_screen("INFO", "No implementado aun.", "ENTER para continuar")
    _pause()


@app.command()
def run(
    is_prod: str | None = typer.Option(
        None,
        "--IS_PROD",
        "--is-prod",
        help="Sobrescribe IS_PROD del .env (true/false).",
    ),
) -> None:
    global _CURRENT_SESSION_ID, _IS_PROD_OVERRIDE
    _IS_PROD_OVERRIDE = _parse_bool_option(is_prod)
    session_id = str(uuid.uuid4())
    _CURRENT_SESSION_ID = session_id
    gateway = _build_product_gateway()
    while True:
        try:
            _clear()
            menu_screen = _main_menu_body()
            mode_label = "PROD" if _is_prod_enabled() else "DEV"
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
    app()
