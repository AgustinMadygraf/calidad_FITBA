"""
Path: run_cli.py
"""

from __future__ import annotations

from typing import Optional, Sequence

from src.interface_adapter.controllers import terminal_cli as _cli

DEFAULT_BASE_URL = _cli.DEFAULT_BASE_URL
DEFAULT_TIMEOUT_SECONDS = _cli.DEFAULT_TIMEOUT_SECONDS
SCREEN_WIDTH = _cli.SCREEN_WIDTH
OFFICIAL_ENTITIES = _cli.OFFICIAL_ENTITIES
ENTITY_ALIASES = _cli.ENTITY_ALIASES
ENTITY_HELP = _cli.ENTITY_HELP
FUNCTION_KEY_COMMANDS = _cli.FUNCTION_KEY_COMMANDS
ENTITY_NUMERIC_MAP = _cli.ENTITY_NUMERIC_MAP
MENU_NUMERIC_COMMANDS = _cli.MENU_NUMERIC_COMMANDS
ENTITY_NUMERIC_HELP = _cli.ENTITY_NUMERIC_HELP
NUMERIC_MENU_HELP = _cli.NUMERIC_MENU_HELP
FUNCTION_KEY_HELP = _cli.FUNCTION_KEY_HELP
COMMAND_ALIASES = _cli.COMMAND_ALIASES

CLIState = _cli.CLIState

build_parser = _cli.build_parser
render_menu = _cli.render_menu
prompt_for = _cli.prompt_for
parse_command = _cli.parse_command
normalize_entity = _cli.normalize_entity
resolve_target_entity = _cli.resolve_target_entity
_trim_for_status = _cli._trim_for_status
_handle_enter = _cli._handle_enter
_read_entity_for_numeric_action = _cli._read_entity_for_numeric_action
_expand_numeric_selection = _cli._expand_numeric_selection


def process_command(
    line: str,
    state: CLIState,
    base_url: str,
    timeout: float,
    *,
    read_input=input,
    write_output=print,
) -> bool:
    return _cli.process_command(
        line,
        state,
        base_url,
        timeout,
        read_input=read_input,
        write_output=write_output,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    return _cli.main(argv, process_command_fn=process_command)


if __name__ == "__main__":
    raise SystemExit(main())
