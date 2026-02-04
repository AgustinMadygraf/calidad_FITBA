import os
from rich.console import Console
from rich.theme import Theme

_theme = Theme(
    {
        "label": "bright_green",
        "field": "green",
        "warn": "yellow",
        "error": "red",
        "dim": "grey66",
    }
)

console = Console(theme=_theme)


class EscapeError(Exception):
    pass


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _prompt(prefix: str) -> str:
    try:
        value = console.input(prefix).strip()
    except KeyboardInterrupt as exc:
        raise EscapeError("Cancelado") from exc
    if "\x1b" in value:
        raise EscapeError("Cancelado")
    return value


def prompt_text(label: str, required: bool = False, default: str | None = None) -> str | None:
    while True:
        prompt = f"[label]{label}[/label]"
        if default is not None:
            prompt += f" [dim][{default}][/dim]"
        prompt += "\n==> "
        value = _prompt(prompt)
        if not value and default is not None:
            value = default
        if required and not value:
            console.print("[error]Campo requerido[/error]")
            continue
        return value if value else None


def prompt_bool(label: str, default: bool = False) -> bool:
    default_str = "S" if default else "N"
    while True:
        value = _prompt(f"[label]{label}[/label] (S/N) [dim][{default_str}][/dim]\n==> ").lower()
        if not value:
            return default
        if value in ("s", "si", "sí", "y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        console.print("[error]Ingrese S o N[/error]")


def prompt_int(label: str, required: bool = True) -> int | None:
    while True:
        value = _prompt(f"[label]{label}[/label]\n==> ")
        if not value and not required:
            return None
        try:
            return int(value)
        except ValueError:
            console.print("[error]Número inválido[/error]")


def confirm(label: str) -> bool:
    return prompt_bool(label, default=False)
