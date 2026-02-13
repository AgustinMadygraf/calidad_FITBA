from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

PRODUCT_ENTITY = "ProductoVentaBean"
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

InputReader = Callable[[str], str]
OutputWriter = Callable[[str], None]


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
class ProductPayloadBuildResult:
    payload: Optional[Dict[str, Any]]
    error_message: Optional[str] = None


@dataclass
class EnterCommandResult:
    ok: bool
    message: str


@dataclass
class EntityActionPlan:
    ok: bool
    target_entity: Optional[str] = None
    is_create_product: bool = False
    error_message: Optional[str] = None


def parse_command(raw: str) -> Tuple[str, list[str]]:
    parts = shlex.split(raw)
    if not parts:
        return "", []
    return parts[0].upper(), parts[1:]


def build_product_payload(
    *,
    nombre: str,
    codigo: str,
    usrcode: str,
    extra_json: str,
) -> ProductPayloadBuildResult:
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
            return ProductPayloadBuildResult(
                payload=None,
                error_message=f"JSON invalido: {exc.msg}",
            )
        if not isinstance(extra, dict):
            return ProductPayloadBuildResult(
                payload=None,
                error_message="payload_json debe ser un objeto JSON.",
            )
        payload.update(extra)

    if not payload:
        return ProductPayloadBuildResult(
            payload=None,
            error_message=EMPTY_PRODUCT_PAYLOAD_MESSAGE,
        )
    return ProductPayloadBuildResult(payload=payload)


def enter_entity(args: list[str], state: CLIState) -> EnterCommandResult:
    if not args:
        return EnterCommandResult(ok=False, message="Uso: ENTER <entity_type>")

    entity = normalize_entity(args[0])
    if entity is None:
        return EnterCommandResult(
            ok=False,
            message=f"Entity type no soportado. Usa: {ENTITY_HELP}",
        )

    state.current_entity = entity
    return EnterCommandResult(ok=True, message=f"Contexto actual: {entity}")


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


def plan_entity_action(command: str, args: list[str], state: CLIState) -> EntityActionPlan:
    target_entity = resolve_target_entity(args, state.current_entity)
    if target_entity is None:
        if not args and state.current_entity is None:
            return EntityActionPlan(
                ok=False,
                error_message="Debes indicar entity_type o usar ENTER <entity_type>.",
            )
        return EntityActionPlan(
            ok=False,
            error_message=f"Entity type no soportado. Usa: {ENTITY_HELP}",
        )

    return EntityActionPlan(
        ok=True,
        target_entity=target_entity,
        is_create_product=(command == "CREATE" and target_entity == PRODUCT_ENTITY),
    )


def read_entity_for_numeric_action(
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


def expand_numeric_selection(
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
        entity = read_entity_for_numeric_action(
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
        entity = read_entity_for_numeric_action(
            state,
            read_input,
            write_output,
            allow_current_on_empty=True,
        )
        if entity is None:
            return None
        return f"{action} {entity}"
    if selection == 6:
        entity = read_entity_for_numeric_action(
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


def resolve_alias_command(
    command: str,
    args: list[str],
    state: CLIState,
) -> Tuple[str, list[str]]:
    canonical = COMMAND_ALIASES.get(command, command)

    if canonical != "DSP":
        return canonical, args

    if len(args) >= 2:
        return "GET", args
    if len(args) == 1:
        return "LIST", args
    if state.current_entity is not None:
        return "LIST", [state.current_entity]
    return "MENU", []
