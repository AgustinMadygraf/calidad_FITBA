from __future__ import annotations

import sys
import uuid
from typing import Any

import httpx
import typer

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


def _product_menu(session_id: str) -> None:
    while True:
        resp = _post_execute(session_id, "ENTER product")
        print(resp["screen"])
        choice = _prompt("> ")
        if choice == "1":
            external_id = _prompt("ID (opcional): ") or None
            name = _prompt("Nombre: ")
            sku = _prompt("SKU (opcional): ") or None
            price_raw = _prompt("Precio (opcional): ") or None
            try:
                price = float(price_raw) if price_raw else None
            except ValueError:
                print("Precio invalido.")
                continue
            args = {"external_id": external_id, "name": name, "sku": sku, "price": price}
            resp = _post_execute(session_id, "CREATE product", args)
            print(resp["screen"])
        elif choice == "2":
            external_id = _prompt("ID: ")
            name = _prompt("Nombre (opcional): ") or None
            sku = _prompt("SKU (opcional): ") or None
            price_raw = _prompt("Precio (opcional): ") or None
            try:
                price = float(price_raw) if price_raw else None
            except ValueError:
                print("Precio invalido.")
                continue
            args = {"external_id": external_id, "name": name, "sku": sku, "price": price}
            resp = _post_execute(session_id, "UPDATE product", args)
            print(resp["screen"])
        elif choice == "3":
            external_id = _prompt("ID: ")
            if settings.xubio_mode == "real" and not _double_confirm():
                print("Baja cancelada.")
                continue
            resp = _post_execute(session_id, "DELETE product", {"external_id": external_id})
            print(resp["screen"])
        elif choice == "4":
            external_id = _prompt("ID: ")
            resp = _post_execute(session_id, "GET product", {"external_id": external_id})
            print(resp["screen"])
        elif choice == "5":
            resp = _post_execute(session_id, "LIST product", {})
            print(resp["screen"])
        elif choice == "6":
            _post_execute(session_id, "BACK")
            return
        else:
            print("Opcion invalida.")


def _stub_screen(session_id: str, entity_type: str) -> None:
    resp = _post_execute(session_id, f"ENTER {entity_type}")
    print(resp["screen"])
    _prompt("")


@app.command()
def run() -> None:
    session_id = str(uuid.uuid4())
    while True:
        resp = _post_execute(session_id, "MENU")
        print(resp["screen"])
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
            print("Opcion invalida.")


if __name__ == "__main__":
    run()
