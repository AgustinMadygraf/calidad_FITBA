from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from src.infrastructure.httpx.token_client import request_with_token
from src.interface_adapter.controllers import terminal_cli as _cli

DEFAULT_BASE_URL = _cli.DEFAULT_BASE_URL
DEFAULT_TIMEOUT_SECONDS = _cli.DEFAULT_TIMEOUT_SECONDS
PRODUCT_CREATE_PATH = _cli.PRODUCT_CREATE_PATH
PRODUCT_ENTITY = _cli.PRODUCT_ENTITY
SCREEN_WIDTH = _cli.SCREEN_WIDTH
EMPTY_PRODUCT_PAYLOAD_MESSAGE = _cli.EMPTY_PRODUCT_PAYLOAD_MESSAGE
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
PostResult = _cli.PostResult

build_parser = _cli.build_parser
render_menu = _cli.render_menu
prompt_for = _cli.prompt_for
parse_command = _cli.parse_command
normalize_entity = _cli.normalize_entity
resolve_target_entity = _cli.resolve_target_entity
build_url = _cli.build_url
_safe_json = _cli._safe_json
_extract_error_detail = _cli._extract_error_detail
_trim_for_status = _cli._trim_for_status
_handle_enter = _cli._handle_enter
_read_entity_for_numeric_action = _cli._read_entity_for_numeric_action
_expand_numeric_selection = _cli._expand_numeric_selection


def collect_product_payload(read_input, write_output):
    return _cli.collect_product_payload(read_input, write_output)


def post_product(base_url: str, payload: Dict[str, Any], timeout: float) -> PostResult:
    return _cli.post_product(
        base_url,
        payload,
        timeout,
        request_executor=request_with_token,
    )


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
        collect_payload_fn=collect_product_payload,
        post_product_fn=post_product,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    return _cli.main(argv, process_command_fn=process_command)


if __name__ == "__main__":
    raise SystemExit(main())
