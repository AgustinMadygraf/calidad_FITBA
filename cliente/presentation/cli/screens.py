from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from cliente.dtos.contact_dto import ContactDTO

_theme = Theme(
    {
        "title": "bold bright_green",
        "label": "bright_green",
        "field": "green",
        "warn": "yellow",
        "error": "red",
        "dim": "grey66",
    }
)

console = Console(theme=_theme)


def header(title: str) -> None:
    console.rule(f"[title]CONTACTOS[/title]  [dim]|[/dim]  [label]{title}[/label]")


def footer(text: str = "ESC=Cancelar  ENTER=Continuar") -> None:
    console.rule(f"[dim]{text}[/dim]")


def contacts_table(contacts: list[ContactDTO]) -> None:
    table = Table(show_lines=False, header_style="label")
    table.add_column("ID", justify="right", style="field")
    table.add_column("NOMBRE", style="field")
    table.add_column("EMAIL", style="field")
    table.add_column("TEL", style="field")
    table.add_column("CLI", style="field")
    table.add_column("PROV", style="field")

    for c in contacts:
        table.add_row(
            str(c.id),
            c.full_name,
            c.email or "",
            c.phone or "",
            "S" if c.is_customer else "N",
            "S" if c.is_supplier else "N",
        )
    console.print(table)


def show_contact(contact: ContactDTO) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("01 ID", str(contact.id))
    table.add_row("02 NOMBRE", contact.full_name)
    table.add_row("03 EMAIL", contact.email or "")
    table.add_row("04 TEL", contact.phone or "")
    table.add_row("05 EMPRESA", contact.company or "")
    table.add_row("06 NOTAS", contact.notes or "")
    table.add_row("07 CLIENTE", "S" if contact.is_customer else "N")
    table.add_row("08 PROVEEDOR", "S" if contact.is_supplier else "N")
    console.print(table)
