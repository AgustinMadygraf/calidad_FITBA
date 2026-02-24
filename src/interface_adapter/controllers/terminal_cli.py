from __future__ import annotations

import argparse
import difflib
import ipaddress
import os
import socket
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, TypeAlias
from urllib.parse import urlparse

from src.infrastructure.sqlite3.network_audit_repository import SqliteNetworkAuditRepository
from src.shared.config import get_network_audit_db_path, load_env
from src.use_cases.network_audit import get_last_network_audit_status
from src.use_cases import terminal_cli as cli_use_case
from src.interface_adapter.presenter import terminal_cli_presenter as cli_presenter

DEFAULT_BASE_URL = os.getenv("CLI_BASE_URL", "https://xubio.com")
DEFAULT_TIMEOUT_SECONDS = 10.0
SCREEN_WIDTH = cli_presenter.SCREEN_WIDTH
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


def _handle_enter(args: list[str], state: CLIState, write_output: OutputWriter) -> None:
    result = cli_use_case.enter_entity(args, state)
    write_output(result.message)


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


def _detect_lan_ips() -> list[str]:
    ips: set[str] = set()
    try:
        host_ips = socket.gethostbyname_ex(socket.gethostname())[2]
        for ip in host_ips:
            if not ip.startswith("127."):
                ips.add(ip)
    except OSError:
        pass
    if not ips:
        try:
            output = os.popen("hostname -I 2>/dev/null").read().strip()
            if output:
                for ip in output.split():
                    if not ip.startswith("127."):
                        ips.add(ip)
        except OSError:
            pass
    return sorted(ips)


def _is_tcp_open(host: str, port: int, timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _classify_ip(ip: str) -> str:
    try:
        parsed = ipaddress.ip_address(ip)
    except ValueError:
        return "desconocida"
    if parsed.is_private:
        return "privada"
    if parsed.is_loopback:
        return "loopback"
    if parsed.is_link_local:
        return "link-local"
    return "publica"


def _handle_network_info_command(_args: list[str], context: CommandContext) -> bool:
    parsed_url = urlparse(context.base_url)
    scheme = (parsed_url.scheme or "http").lower()
    host = parsed_url.hostname or "-"
    resolved_port = parsed_url.port
    if resolved_port is None:
        resolved_port = 443 if scheme == "https" else 80

    lan_ips = _detect_lan_ips()
    if lan_ips:
        lan_summary = ", ".join(f"{ip} ({_classify_ip(ip)})" for ip in lan_ips)
    else:
        lan_summary = "No detectada"
    audit = get_last_network_audit_status(
        SqliteNetworkAuditRepository(get_network_audit_db_path())
    )
    if audit is None:
        audit_summary = "sin registros"
        audit_db = "no disponible"
    else:
        audit_summary = (
            f"lan_ip={audit.current.lan_ip} "
            f"changed_ip={'si' if audit.changed_ip else 'no'} "
            f"changed_iface={'si' if audit.changed_iface else 'no'} "
            f"changed_gw={'si' if audit.changed_gw else 'no'}"
        )
        audit_db = audit.db_path

    lines = [
        "Diagnostico de red y HTTPS",
        f"- Hostname: {socket.gethostname()}",
        f"- FQDN: {socket.getfqdn()}",
        f"- IPs LAN detectadas: {lan_summary}",
        f"- CLI base_url: {context.base_url}",
        f"- Base URL esquema: {scheme.upper()}",
        f"- Base URL host: {host}",
        f"- Base URL puerto: {resolved_port}",
        f"- Puerto local 8000 abierto: {'si' if _is_tcp_open('127.0.0.1', 8000) else 'no'}",
        f"- Puerto local 443 abierto: {'si' if _is_tcp_open('127.0.0.1', 443) else 'no'}",
        f"- SQLite network audit: {audit_summary}",
        f"- SQLite network audit db: {audit_db}",
        "",
        "Sugerencias:",
        "- Publicar frontend contra un hostname estable (DNS interno), no contra IP hardcodeada.",
        "- Si necesitas HTTPS en LAN, terminar TLS en :443 (Nginx/Caddy) y hacer proxy a FastAPI :8000.",
        "- Pedir a IT reserva DHCP/IP fija para el servidor para evitar cambios de URL por red.",
    ]
    context.write_output("\n".join(lines))
    return False


def _handle_exit_command(_args: list[str], _context: CommandContext) -> bool:
    return True


def _handle_entity_action(
    command: str,
    args: list[str],
    context: CommandContext,
) -> bool:
    plan = cli_use_case.plan_entity_action(command, args, context.state)
    if not plan.ok:
        if plan.error_message is not None:
            context.write_output(plan.error_message)
        return False

    context.write_output(f"MVP: {command} {plan.target_entity} esta en modo stub.")
    return False


def _make_entity_handler(
    command: str,
) -> CommandHandler:
    def _handler(args: list[str], context: CommandContext) -> bool:
        return _handle_entity_action(command, args, context)

    return _handler


def _build_command_handlers(
) -> Dict[str, CommandHandler]:
    return {
        "MENU": _handle_menu_command,
        "NETINFO": _handle_network_info_command,
        "ENTER": _handle_enter_command,
        "BACK": _handle_back_command,
        "EXIT": _handle_exit_command,
        "GET": _make_entity_handler("GET"),
        "LIST": _make_entity_handler("LIST"),
    }


def process_command(
    line: str,
    state: CLIState,
    base_url: str,
    timeout: float,
    *,
    read_input: InputReader = input,
    write_output: OutputWriter = print,
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
    if canonical_command == "RED":
        canonical_command = "NETINFO"
    handlers = _build_command_handlers()
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
            print("\nSaliendo de CLI")
            break

        should_exit = command_runner(
            line,
            state,
            args.base_url,
            args.timeout,
            write_output=_status_write,
        )
        if should_exit:
            print("Saliendo de CLI")
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
