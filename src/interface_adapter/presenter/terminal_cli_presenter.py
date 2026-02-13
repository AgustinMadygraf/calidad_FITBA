from __future__ import annotations

from ...use_cases.terminal_cli import (
    CLIState,
    ENTITY_HELP,
)

SCREEN_WIDTH = 64
CLI_TITLE = "XUBIO CLI (MVP)"


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
        CLI_TITLE,
        f"API: {api_value}",
        f"Contexto: {current_entity}",
        f"Estado: {status}",
        "",
        "Comandos:",
        "  MENU | HELP",
        "  ENTER <entity_type>",
        "  CREATE <entity_type>",
        "  UPDATE <entity_type>",
        "  DELETE <entity_type>",
        "  GET <entity_type> <id>",
        "  LIST <entity_type>",
        "  BACK",
        "  EXIT | QUIT | SALIR",
        "",
        "Abreviaturas: CR=CREATE DLT=DELETE DSP=LIST/GET",
        f"Entity types: {ENTITY_HELP}",
        "Atajos numericos/function-key: deshabilitados",
        "",
        "Ejemplos:",
        "  ENTER ProductoVentaBean",
        "  CREATE",
        "  DSP ProductoVentaBean 55",
        "",
        "MVP: solo CREATE ProductoVentaBean ejecuta POST real.",
    ]
    return "\n".join(lines)


def prompt_for(state: CLIState) -> str:
    context = (state.current_entity or "menu").strip()
    return f"xubio[{context}]> "
