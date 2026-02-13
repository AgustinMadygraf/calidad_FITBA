from __future__ import annotations

import argparse
import difflib
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, TypeAlias

from ...infrastructure.httpx import terminal_cli_gateway_xubio as cli_gateway
from ...shared.config import load_env
from ...use_cases import terminal_cli as cli_use_case
from ...use_cases import terminal_cli_product as cli_product_use_case
from ..presenter import terminal_cli_presenter as cli_presenter

DEFAULT_BASE_URL = os.getenv("CLI_BASE_URL", "https://xubio.com")
DEFAULT_TIMEOUT_SECONDS = 10.0
PRODUCT_CREATE_PATH = cli_gateway.PRODUCT_CREATE_PATH
PRODUCT_ENTITY = cli_use_case.PRODUCT_ENTITY
SCREEN_WIDTH = cli_presenter.SCREEN_WIDTH
EMPTY_PRODUCT_PAYLOAD_MESSAGE = cli_use_case.EMPTY_PRODUCT_PAYLOAD_MESSAGE
OFFICIAL_ENTITIES = cli_use_case.OFFICIAL_ENTITIES
ENTITY_ALIASES = cli_use_case.ENTITY_ALIASES
ENTITY_HELP = cli_use_case.ENTITY_HELP
FUNCTION_KEY_COMMANDS = cli_use_case.FUNCTION_KEY_COMMANDS
ENTITY_NUMERIC_MAP = cli_use_case.ENTITY_NUMERIC_MAP
MENU_NUMERIC_COMMANDS = cli_use_case.MENU_NUMERIC_COMMANDS
ENTITY_NUMERIC_HELP = cli_use_case.ENTITY_NUMERIC_HELP
NUMERIC_MENU_HELP = cli_use_case.NUMERIC_MENU_HELP
FUNCTION_KEY_HELP = cli_use_case.FUNCTION_KEY_HELP
COMMAND_ALIASES = cli_use_case.COMMAND_ALIASES

InputReader = cli_use_case.InputReader
OutputWriter = cli_use_case.OutputWriter
CLIState = cli_use_case.CLIState
PostResult = cli_use_case.PostResult

render_menu = cli_presenter.render_menu
prompt_for = cli_presenter.prompt_for
_trim_for_status = cli_presenter.trim_for_status

parse_command = cli_use_case.parse_command
normalize_entity = cli_use_case.normalize_entity
resolve_target_entity = cli_use_case.resolve_target_entity
_read_entity_for_numeric_action = cli_use_case.read_entity_for_numeric_action
_expand_numeric_selection = cli_use_case.expand_numeric_selection
_resolve_alias_command = cli_use_case.resolve_alias_command

build_url = cli_gateway.build_url
_safe_json = cli_gateway.safe_json
_extract_error_detail = cli_gateway.extract_error_detail

CollectPayloadFn: TypeAlias = Callable[[InputReader, OutputWriter], Optional[Dict[str, Any]]]
PostProductFn: TypeAlias = Callable[[str, Dict[str, Any], float], PostResult]
ProcessCommandFn: TypeAlias = Callable[..., bool]


@dataclass
class CommandContext:
    state: CLIState
    base_url: str
    timeout: float
    read_input: InputReader
    write_output: OutputWriter


CommandHandler: TypeAlias = Callable[[list[str], CommandContext], bool]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Xubio CLI interactiva (MVP)."
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
        help="Inicia sin imprimir la ayuda inicial del CLI.",
    )
    return parser


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
    result = cli_use_case.build_product_payload(
        nombre=nombre,
        codigo=codigo,
        usrcode=usrcode,
        extra_json=extra_json,
    )
    if result.error_message is not None:
        write_output(result.error_message)
        return None
    return result.payload


def post_product(
    base_url: str,
    payload: Dict[str, Any],
    timeout: float,
    request_executor: Optional[Callable[..., Any]] = None,
) -> PostResult:
    gateway = cli_gateway.XubioTerminalCliProductGateway(
        request_executor=request_executor,
    )
    return cli_product_use_case.create_product(
        gateway,
        base_url=base_url,
        payload=payload,
        timeout=timeout,
    )


def _handle_enter(args: list[str], state: CLIState, write_output: OutputWriter) -> None:
    result = cli_use_case.enter_entity(args, state)
    write_output(result.message)


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
        write_output(_render_json_payload(result.payload))


def _render_json_payload(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


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
    plan = cli_use_case.plan_entity_action(command, args, context.state)
    if not plan.ok:
        if plan.error_message is not None:
            context.write_output(plan.error_message)
        return False

    if plan.is_create_product:
        _handle_create_product(
            context.base_url,
            context.timeout,
            context.read_input,
            context.write_output,
            collect_payload_fn,
            post_product_fn,
        )
        return False

    context.write_output(f"MVP: {command} {plan.target_entity} esta en modo stub.")
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
        suggestion = _suggest_command(command, handlers.keys())
        if suggestion is None:
            write_output(f"Comando no reconocido: {command}. Usa HELP para ayuda.")
        else:
            write_output(
                f"Comando no reconocido: {command}. Quisiste decir {suggestion}? "
                "Usa HELP para ayuda."
            )
        return False

    context = CommandContext(
        state=state,
        base_url=base_url,
        timeout=timeout,
        read_input=read_input,
        write_output=write_output,
    )
    return handler(canonical_args, context)


def _suggest_command(command: str, options: Any) -> Optional[str]:
    candidates = list(options)
    matches = difflib.get_close_matches(command.upper(), candidates, n=1, cutoff=0.6)
    if not matches:
        return None
    return matches[0]


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
