from __future__ import annotations

import argparse
import json
import os
import shlex
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

import httpx

from src.shared.config import load_env

DEFAULT_BASE_URL = os.getenv("CLI_BASE_URL", "http://localhost:8000")
DEFAULT_TIMEOUT_SECONDS = 10.0
PRODUCT_CREATE_PATH = "/API/1.1/ProductoVentaBean"

ENTITY_ALIASES = {
    "product": "product",
    "producto": "product",
    "client": "client",
    "cliente": "client",
    "remito": "remito",
    "lista_precio": "lista_precio",
    "listaprecio": "lista_precio",
}

ENTITY_HELP = "product, client, remito, lista_precio"


@dataclass
class CLIState:
    current_entity: Optional[str] = None


@dataclass
class PostResult:
    ok: bool
    status_code: Optional[int]
    message: str
    payload: Optional[Dict[str, Any]] = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AS400-like terminal client (MVP) for local Xubio-like API."
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"HTTP timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Start without printing the AS400 menu banner.",
    )
    return parser


def render_menu(state: CLIState, base_url: str) -> str:
    current_entity = state.current_entity or "-"
    lines = [
        "+----------------------------------------------------------------+",
        "| XUBIO-LIKE TERMINAL (AS400 MVP)                                |",
        f"| API: {base_url:<58}|",
        f"| CURRENT ENTITY: {current_entity:<47}|",
        "|----------------------------------------------------------------|",
        "| MENU                                                           |",
        "| ENTER <entity_type>                                            |",
        "| CREATE <entity_type>                                           |",
        "| UPDATE <entity_type>                                            |",
        "| DELETE <entity_type>                                            |",
        "| GET <entity_type> <id>                                          |",
        "| LIST <entity_type>                                              |",
        "| BACK                                                           |",
        "| EXIT                                                           |",
        "+----------------------------------------------------------------+",
        f"Entity types: {ENTITY_HELP}",
        "MVP activo: solo CREATE product realiza POST real.",
    ]
    return "\n".join(lines)


def prompt_for(state: CLIState) -> str:
    return f"{(state.current_entity or 'MENU').upper()}> "


def parse_command(raw: str) -> Tuple[str, list[str]]:
    parts = shlex.split(raw)
    if not parts:
        return "", []
    return parts[0].upper(), parts[1:]


def normalize_entity(raw: str) -> Optional[str]:
    return ENTITY_ALIASES.get(raw.strip().lower())


def resolve_target_entity(args: list[str], current_entity: Optional[str]) -> Optional[str]:
    if args:
        return normalize_entity(args[0])
    return current_entity


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def collect_product_payload(
    read_input: Callable[[str], str], write_output: Callable[[str], None]
) -> Optional[Dict[str, Any]]:
    nombre = read_input("nombre (requerido): ").strip()
    if not nombre:
        write_output("CREATE product cancelado: nombre es requerido.")
        return None

    codigo = read_input("codigo (opcional): ").strip()
    usrcode = read_input("usrcode (opcional): ").strip()
    extra_json = read_input("extra_json objeto (opcional): ").strip()

    payload: Dict[str, Any] = {"nombre": nombre}
    if codigo:
        payload["codigo"] = codigo
    if usrcode:
        payload["usrcode"] = usrcode

    if extra_json:
        try:
            extra = json.loads(extra_json)
        except json.JSONDecodeError as exc:
            write_output(f"JSON invalido: {exc.msg}")
            return None
        if not isinstance(extra, dict):
            write_output("extra_json debe ser un objeto JSON.")
            return None
        payload.update(extra)

    return payload


def post_product(base_url: str, payload: Dict[str, Any], timeout: float) -> PostResult:
    url = build_url(base_url, PRODUCT_CREATE_PATH)
    try:
        response = httpx.post(url, json=payload, timeout=timeout)
    except httpx.HTTPError as exc:
        return PostResult(
            ok=False,
            status_code=None,
            message=f"Error HTTP al crear producto: {exc}",
            payload=None,
        )

    raw_payload = _safe_json(response)
    payload_dict = raw_payload if isinstance(raw_payload, dict) else None

    if 200 <= response.status_code < 300:
        return PostResult(
            ok=True,
            status_code=response.status_code,
            message=f"Producto creado correctamente (HTTP {response.status_code}).",
            payload=payload_dict,
        )

    detail = _extract_error_detail(raw_payload, response)
    if response.status_code == 403:
        message = (
            "Operacion rechazada (HTTP 403). Para crear productos, el server "
            "debe correr con IS_PROD=true."
        )
    elif detail:
        message = f"Error al crear producto (HTTP {response.status_code}): {detail}"
    else:
        message = f"Error al crear producto (HTTP {response.status_code})."

    return PostResult(
        ok=False,
        status_code=response.status_code,
        message=message,
        payload=payload_dict,
    )


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _extract_error_detail(raw_payload: Any, response: httpx.Response) -> str:
    if isinstance(raw_payload, dict):
        detail = raw_payload.get("detail")
        if detail is not None:
            return str(detail)
    text = getattr(response, "text", "")
    return text.strip()[:300]


def _handle_enter(args: list[str], state: CLIState, write_output: Callable[[str], None]) -> None:
    if not args:
        write_output("Uso: ENTER <entity_type>")
        return
    entity = normalize_entity(args[0])
    if entity is None:
        write_output(f"Entity type no soportado. Usa: {ENTITY_HELP}")
        return
    state.current_entity = entity
    write_output(f"Contexto actual: {entity}")


def _handle_create_product(
    base_url: str,
    timeout: float,
    read_input: Callable[[str], str],
    write_output: Callable[[str], None],
) -> None:
    payload = collect_product_payload(read_input, write_output)
    if payload is None:
        return
    result = post_product(base_url, payload, timeout)
    write_output(result.message)
    if result.payload is not None:
        write_output(json.dumps(result.payload, indent=2, sort_keys=True))


def process_command(
    line: str,
    state: CLIState,
    base_url: str,
    timeout: float,
    *,
    read_input: Callable[[str], str] = input,
    write_output: Callable[[str], None] = print,
) -> bool:
    try:
        command, args = parse_command(line)
    except ValueError as exc:
        write_output(f"Error de sintaxis: {exc}")
        return False

    if not command:
        return False

    if command in {"EXIT", "QUIT", "SALIR"}:
        return True

    if command in {"MENU", "HELP"}:
        write_output(render_menu(state, base_url))
        return False

    if command == "ENTER":
        _handle_enter(args, state, write_output)
        return False

    if command == "BACK":
        state.current_entity = None
        write_output("Volviste al menu principal.")
        return False

    if command in {"CREATE", "UPDATE", "DELETE", "GET", "LIST"}:
        target_entity = resolve_target_entity(args, state.current_entity)
        if target_entity is None:
            if not args and state.current_entity is None:
                write_output("Debes indicar entity_type o usar ENTER <entity_type>.")
            else:
                write_output(f"Entity type no soportado. Usa: {ENTITY_HELP}")
            return False

        if command == "CREATE" and target_entity == "product":
            _handle_create_product(base_url, timeout, read_input, write_output)
            return False

        write_output(f"MVP: {command} {target_entity} esta en modo stub.")
        return False

    write_output(f"Comando no reconocido: {command}. Usa MENU para ayuda.")
    return False


def main(argv: Optional[Sequence[str]] = None) -> int:
    load_env()
    parser = build_parser()
    args = parser.parse_args(argv)

    state = CLIState()
    if not args.no_banner:
        print(render_menu(state, args.base_url))

    while True:
        try:
            line = input(prompt_for(state))
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo de run_cli.py")
            break

        should_exit = process_command(
            line,
            state,
            args.base_url,
            args.timeout,
        )
        if should_exit:
            print("Saliendo de run_cli.py")
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
