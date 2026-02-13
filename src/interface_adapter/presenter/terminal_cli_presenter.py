from __future__ import annotations

from ...use_cases.terminal_cli import (
    CLIState,
    ENTITY_HELP,
    ENTITY_NUMERIC_HELP,
    FUNCTION_KEY_HELP,
    NUMERIC_MENU_HELP,
)

SCREEN_WIDTH = 64


def trim_for_status(text: str, max_chars: int = 55) -> str:
    clean = (text or "").replace("\n", " ").strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3] + "..."


def render_menu(state: CLIState, base_url: str) -> str:
    api_value = trim_for_status(base_url, max_chars=58)
    current_entity = trim_for_status(state.current_entity or "-", max_chars=47)
    status = trim_for_status(state.last_status, max_chars=55)
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
