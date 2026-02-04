import os
from rich.console import Console

console = Console()


class EscapeError(Exception):
    pass


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def prompt_text(label: str, required: bool = False, default: str | None = None) -> str | None:
    while True:
        prompt = f"{label}"
        if default is not None:
            prompt += f" [{default}]"
        prompt += ": "
        try:
            value = console.input(prompt).strip()
        except KeyboardInterrupt as exc:
            raise EscapeError("Cancelado") from exc
        if "\x1b" in value:
            raise EscapeError("Cancelado")
        if not value and default is not None:
            value = default
        if required and not value:
            console.print("[red]Campo requerido[/red]")
            continue
        return value if value else None


def prompt_bool(label: str, default: bool = False) -> bool:
    default_str = "S" if default else "N"
    while True:
        try:
            value = console.input(f"{label} (S/N) [{default_str}]: ").strip().lower()
        except KeyboardInterrupt as exc:
            raise EscapeError("Cancelado") from exc
        if "\x1b" in value:
            raise EscapeError("Cancelado")
        if not value:
            return default
        if value in ("s", "si", "sí", "y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        console.print("[red]Ingrese S o N[/red]")


def prompt_int(label: str, required: bool = True) -> int | None:
    while True:
        try:
            value = console.input(f"{label}: ").strip()
        except KeyboardInterrupt as exc:
            raise EscapeError("Cancelado") from exc
        if "\x1b" in value:
            raise EscapeError("Cancelado")
        if not value and not required:
            return None
        try:
            return int(value)
        except ValueError:
            console.print("[red]Número inválido[/red]")


def confirm(label: str) -> bool:
    return prompt_bool(label, default=False)
