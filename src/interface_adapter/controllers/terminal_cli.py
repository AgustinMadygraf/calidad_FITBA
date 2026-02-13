from __future__ import annotations

import argparse
import json
import os
import shlex
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, TypeAlias

import httpx

from ...infrastructure.httpx.token_client import request_with_token
from ...shared.config import load_env

DEFAULT_BASE_URL = os.getenv("CLI_BASE_URL", "https://xubio.com")
DEFAULT_TIMEOUT_SECONDS = 10.0
PRODUCT_CREATE_PATH = "/API/1.1/ProductoVentaBean"
PRODUCT_ENTITY = "ProductoVentaBean"
SCREEN_WIDTH = 64
EMPTY_PRODUCT_PAYLOAD_MESSAGE = (
    "Debes ingresar al menos un campo para crear ProductoVentaBean."
)
OFFICIAL_ENTITIES = [
    "ProductoVentaBean",
    "clienteBean",
    "remitoVentaBean",
    "listaPrecioBean",
]

ENTITY_ALIASES = {
    "productoventabean": "ProductoVentaBean",
    "clientebean": "clienteBean",
    "remitoventabean": "remitoVentaBean",
    "listapreciobean": "listaPrecioBean",
}
ENTITY_HELP = "ProductoVentaBean, clienteBean, remitoVentaBean, listaPrecioBean"
FUNCTION_KEY_COMMANDS = {
    "F1": "MENU",
    "F3": "EXIT",
    "F12": "BACK",
}
ENTITY_NUMERIC_MAP = {
    1: "ProductoVentaBean",
    2: "clienteBean",
    3: "remitoVentaBean",
    4: "listaPrecioBean",
}
MENU_NUMERIC_COMMANDS = {
    1: "MENU",
    2: "ENTER",
    3: "CREATE",
    4: "UPDATE",
    5: "DELETE",
    6: "GET",
    7: "LIST",
    8: "BACK",
    9: "EXIT",
}
ENTITY_NUMERIC_HELP = " ".join(f"{idx}={entity}" for idx, entity in ENTITY_NUMERIC_MAP.items())
NUMERIC_MENU_HELP = " ".join(f"{idx}={command}" for idx, command in MENU_NUMERIC_COMMANDS.items())
FUNCTION_KEY_HELP = " ".join(f"{key}={command}" for key, command in FUNCTION_KEY_COMMANDS.items())
COMMAND_ALIASES = {
    "HELP": "MENU",
    "QUIT": "EXIT",
    "SALIR": "EXIT",
    "CR": "CREATE",
    "DLT": "DELETE",
    "DSP": "DSP",
}

InputReader: TypeAlias = Callable[[str], str]
OutputWriter: TypeAlias = Callable[[str], None]


@dataclass
class CLIState:
    current_entity: Optional[str] = None
    last_status: str = "LISTO"


@dataclass
class PostResult:
    ok: bool
    status_code: Optional[int]
    message: str
    payload: Optional[Dict[str, Any]] = None


@dataclass
class CommandContext:
    state: CLIState
    base_url: str
    timeout: float
    read_input: InputReader
    write_output: OutputWriter


CommandHandler: TypeAlias = Callable[[list[str], CommandContext], bool]
CollectPayloadFn: TypeAlias = Callable[[InputReader, OutputWriter], Optional[Dict[str, Any]]]
PostProductFn: TypeAlias = Callable[[str, Dict[str, Any], float], PostResult]
ProcessCommandFn: TypeAlias = Callable[..., bool]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AS400-like terminal client (MVP) for Xubio API."
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
    api_value = _trim_for_status(base_url, max_chars=58)
    current_entity = _trim_for_status(state.current_entity or "-", max_chars=47)
    status = _trim_for_status(state.last_status, max_chars=55)
    lines = [
        f"+{'-' * SCREEN_WIDTH}+",
        "| XUBIO-LIKE TERMINAL (AS400 MVP)                                |",
        f"| API: {api_value:<58}|",
        f"| CURRENT ENTITY: {current_entity:<47}|",
        f"| STATUS: {status:<55}|",
        f"|{'-' * SCREEN_WIDTH}|",
        "| 1) MENU                                                        |",
        "| 2) ENTER <entity_type>                                         |",
        "| 3) CREATE <entity_type>                                        |",
        "| 4) UPDATE <entity_type>                                        |",
        "| 5) DELETE <entity_type>                                        |",
        "| 6) GET <entity_type> <id>                                      |",
        "| 7) LIST <entity_type>                                          |",
        "| 8) BACK                                                        |",
        "| 9) EXIT                                                        |",
        "| CMD ==> escribe opcion numerica o comando textual              |",
        f"+{'-' * SCREEN_WIDTH}+",
        f"Entity types: {ENTITY_HELP}",
        f"Atajos entity_type: {ENTITY_NUMERIC_HELP}",
        f"Atajos numericos: {NUMERIC_MENU_HELP}",
        f"Teclas AS400-like: {FUNCTION_KEY_HELP}",
        "Abreviaturas: CR=CREATE DLT=DELETE DSP=LIST/GET",
        "MVP activo: solo CREATE ProductoVentaBean realiza POST real.",
    ]
    return "\n".join(lines)


def prompt_for(state: CLIState) -> str:
    return f"{(state.current_entity or 'MENU').upper()} ==> "


def parse_command(raw: str) -> Tuple[str, list[str]]:
    parts = shlex.split(raw)
    if not parts:
        return "", []
    return parts[0].upper(), parts[1:]


def normalize_entity(raw: str) -> Optional[str]:
    value = raw.strip()
    if not value:
        return None

    if value.isdigit():
        idx = int(value) - 1
        if 0 <= idx < len(OFFICIAL_ENTITIES):
            return OFFICIAL_ENTITIES[idx]
        return None

    return ENTITY_ALIASES.get(value.lower())


def resolve_target_entity(args: list[str], current_entity: Optional[str]) -> Optional[str]:
    if args:
        return normalize_entity(args[0])
    return current_entity


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def collect_product_payload(
    read_input: InputReader,
    write_output: OutputWriter,
) -> Optional[Dict[str, Any]]:
    nombre = read_input("nombre (opcional): ").strip()
    codigo = read_input("codigo (opcional): ").strip()
    usrcode = read_input("usrcode (opcional): ").strip()
    extra_json = read_input(
        "payload_json objeto (opcional, merge con campos cargados): "
    ).strip()

    payload: Dict[str, Any] = {}
    if nombre:
        payload["nombre"] = nombre
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
            write_output("payload_json debe ser un objeto JSON.")
            return None
        payload.update(extra)

    if not payload:
        write_output(EMPTY_PRODUCT_PAYLOAD_MESSAGE)
        return None

    return payload


def post_product(
    base_url: str,
    payload: Dict[str, Any],
    timeout: float,
    request_executor: Optional[Callable[..., httpx.Response]] = None,
) -> PostResult:
    url = build_url(base_url, PRODUCT_CREATE_PATH)
    request_fn = request_executor or request_with_token
    try:
        response = request_fn("POST", url, json=payload, timeout=timeout)
    except httpx.HTTPError as exc:
        return PostResult(
            ok=False,
            status_code=None,
            message=f"Error HTTP al crear producto: {exc}",
            payload=None,
        )
    except RuntimeError as exc:
        return PostResult(
            ok=False,
            status_code=None,
            message=f"Error OAuth2 al crear producto: {exc}",
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
            "Operacion rechazada (HTTP 403): revisa permisos/token OAuth2 o "
            "politicas del servidor destino."
        )
    elif response.status_code == 401:
        message = (
            "No autorizado (HTTP 401): revisa credenciales OAuth2 "
            "(client-id/secret-id/access_token)."
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


def _trim_for_status(text: str, max_chars: int = 55) -> str:
    clean = (text or "").replace("\n", " ").strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3] + "..."


def _handle_enter(args: list[str], state: CLIState, write_output: OutputWriter) -> None:
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
    read_input: InputReader,
    write_output: OutputWriter,
    collect_payload_fn: CollectPayloadFn = collect_product_payload,
    post_product_fn: PostProductFn = post_product,
) -> None:
    payload = collect_payload_fn(read_input, write_output)
    if payload is None:
        return
    if not payload:
        write_output(EMPTY_PRODUCT_PAYLOAD_MESSAGE)
        return
    result = post_product_fn(base_url, payload, timeout)
    write_output(result.message)
    if result.payload is not None:
        write_output(json.dumps(result.payload, indent=2, sort_keys=True))


def _read_entity_for_numeric_action(
    state: CLIState,
    read_input: InputReader,
    write_output: OutputWriter,
    *,
    allow_current_on_empty: bool = True,
) -> Optional[str]:
    if allow_current_on_empty:
        entity_input = read_input(
            f"entity_type oficial [{ENTITY_NUMERIC_HELP}] (vacio = actual): "
        ).strip()
        if not entity_input and state.current_entity:
            return state.current_entity
    else:
        entity_input = read_input(
            f"entity_type oficial [{ENTITY_NUMERIC_HELP}]: "
        ).strip()

    if not entity_input:
        write_output("Debes indicar un entity_type oficial.")
        return None

    entity = normalize_entity(entity_input)
    if entity is None:
        write_output(f"Entity type no soportado. Usa: {ENTITY_HELP}")
        return None
    return entity


def _expand_numeric_selection(
    line: str,
    state: CLIState,
    *,
    read_input: InputReader,
    write_output: OutputWriter,
) -> Optional[str]:
    raw = line.strip()
    upper_raw = raw.upper()
    if upper_raw in FUNCTION_KEY_COMMANDS:
        return FUNCTION_KEY_COMMANDS[upper_raw]
    if not raw.isdigit():
        return line

    selection = int(raw)
    if selection == 1:
        return MENU_NUMERIC_COMMANDS[1]
    if selection == 2:
        entity = _read_entity_for_numeric_action(
            state,
            read_input,
            write_output,
            allow_current_on_empty=False,
        )
        if entity is None:
            return None
        return f"{MENU_NUMERIC_COMMANDS[2]} {entity}"
    if selection in {3, 4, 5, 7}:
        action = MENU_NUMERIC_COMMANDS[selection]
        entity = _read_entity_for_numeric_action(
            state,
            read_input,
            write_output,
            allow_current_on_empty=True,
        )
        if entity is None:
            return None
        return f"{action} {entity}"
    if selection == 6:
        entity = _read_entity_for_numeric_action(
            state,
            read_input,
            write_output,
            allow_current_on_empty=True,
        )
        if entity is None:
            return None
        item_id = read_input("id: ").strip()
        if not item_id:
            write_output("Debes indicar id.")
            return None
        return f"{MENU_NUMERIC_COMMANDS[6]} {entity} {item_id}"
    if selection == 8:
        return MENU_NUMERIC_COMMANDS[8]
    if selection == 9:
        return MENU_NUMERIC_COMMANDS[9]

    write_output(
        "Opcion numerica invalida. Usa 1..9 o MENU para ver comandos disponibles."
    )
    return None


def _handle_menu_command(_args: list[str], context: CommandContext) -> bool:
    context.write_output(render_menu(context.state, context.base_url))
    return False


def _handle_enter_command(args: list[str], context: CommandContext) -> bool:
    _handle_enter(args, context.state, context.write_output)
    return False


def _handle_back_command(_args: list[str], context: CommandContext) -> bool:
    context.state.current_entity = None
    context.write_output("Volviste al menu principal.")
    return False


def _handle_exit_command(_args: list[str], _context: CommandContext) -> bool:
    return True


def _handle_entity_action(
    command: str,
    args: list[str],
    context: CommandContext,
    *,
    collect_payload_fn: CollectPayloadFn = collect_product_payload,
    post_product_fn: PostProductFn = post_product,
) -> bool:
    target_entity = resolve_target_entity(args, context.state.current_entity)
    if target_entity is None:
        if not args and context.state.current_entity is None:
            context.write_output("Debes indicar entity_type o usar ENTER <entity_type>.")
        else:
            context.write_output(f"Entity type no soportado. Usa: {ENTITY_HELP}")
        return False

    if command == "CREATE" and target_entity == PRODUCT_ENTITY:
        _handle_create_product(
            context.base_url,
            context.timeout,
            context.read_input,
            context.write_output,
            collect_payload_fn,
            post_product_fn,
        )
        return False

    context.write_output(f"MVP: {command} {target_entity} esta en modo stub.")
    return False


def _make_entity_handler(
    command: str,
    *,
    collect_payload_fn: CollectPayloadFn = collect_product_payload,
    post_product_fn: PostProductFn = post_product,
) -> CommandHandler:
    def _handler(args: list[str], context: CommandContext) -> bool:
        return _handle_entity_action(
            command,
            args,
            context,
            collect_payload_fn=collect_payload_fn,
            post_product_fn=post_product_fn,
        )

    return _handler


def _build_command_handlers(
    *,
    collect_payload_fn: CollectPayloadFn = collect_product_payload,
    post_product_fn: PostProductFn = post_product,
) -> Dict[str, CommandHandler]:
    return {
        "MENU": _handle_menu_command,
        "ENTER": _handle_enter_command,
        "BACK": _handle_back_command,
        "EXIT": _handle_exit_command,
        "CREATE": _make_entity_handler(
            "CREATE",
            collect_payload_fn=collect_payload_fn,
            post_product_fn=post_product_fn,
        ),
        "UPDATE": _make_entity_handler(
            "UPDATE",
            collect_payload_fn=collect_payload_fn,
            post_product_fn=post_product_fn,
        ),
        "DELETE": _make_entity_handler(
            "DELETE",
            collect_payload_fn=collect_payload_fn,
            post_product_fn=post_product_fn,
        ),
        "GET": _make_entity_handler(
            "GET",
            collect_payload_fn=collect_payload_fn,
            post_product_fn=post_product_fn,
        ),
        "LIST": _make_entity_handler(
            "LIST",
            collect_payload_fn=collect_payload_fn,
            post_product_fn=post_product_fn,
        ),
    }


def _resolve_alias_command(
    command: str,
    args: list[str],
    state: CLIState,
) -> Tuple[str, list[str]]:
    canonical = COMMAND_ALIASES.get(command, command)

    # AS400-like DSP shortcut:
    # - DSP <entity> <id> -> GET <entity> <id>
    # - DSP <entity> -> LIST <entity>
    # - DSP -> LIST <current_entity> or MENU when no context
    if canonical != "DSP":
        return canonical, args

    if len(args) >= 2:
        return "GET", args
    if len(args) == 1:
        return "LIST", args
    if state.current_entity is not None:
        return "LIST", [state.current_entity]
    return "MENU", []


def process_command(
    line: str,
    state: CLIState,
    base_url: str,
    timeout: float,
    *,
    read_input: InputReader = input,
    write_output: OutputWriter = print,
    collect_payload_fn: CollectPayloadFn = collect_product_payload,
    post_product_fn: PostProductFn = post_product,
) -> bool:
    expanded_line = _expand_numeric_selection(
        line,
        state,
        read_input=read_input,
        write_output=write_output,
    )
    if expanded_line is None:
        return False

    try:
        command, args = parse_command(expanded_line)
    except ValueError as exc:
        write_output(f"Error de sintaxis: {exc}")
        return False

    if not command:
        return False

    canonical_command, canonical_args = _resolve_alias_command(command, args, state)
    handlers = _build_command_handlers(
        collect_payload_fn=collect_payload_fn,
        post_product_fn=post_product_fn,
    )
    handler = handlers.get(canonical_command)
    if handler is None:
        write_output(f"Comando no reconocido: {command}. Usa MENU para ayuda.")
        return False

    context = CommandContext(
        state=state,
        base_url=base_url,
        timeout=timeout,
        read_input=read_input,
        write_output=write_output,
    )
    return handler(canonical_args, context)


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    process_command_fn: Optional[ProcessCommandFn] = None,
) -> int:
    load_env()
    parser = build_parser()
    args = parser.parse_args(argv)

    state = CLIState()
    if not args.no_banner:
        print(render_menu(state, args.base_url))

    def _status_write(message: str) -> None:
        state.last_status = (message or "").strip() or "LISTO"
        print(message)

    command_runner = process_command if process_command_fn is None else process_command_fn

    while True:
        try:
            line = input(prompt_for(state))
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo de run_cli.py")
            break

        should_exit = command_runner(
            line,
            state,
            args.base_url,
            args.timeout,
            write_output=_status_write,
        )
        if should_exit:
            print("Saliendo de run_cli.py")
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
