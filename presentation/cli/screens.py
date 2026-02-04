from rich.console import Console
from rich.table import Table
from application.dtos.contact_dto import ContactDTO

console = Console()


def header(title: str) -> None:
    console.rule(f"[bold]Contactos[/bold] - {title}")


def contacts_table(contacts: list[ContactDTO]) -> None:
    table = Table(show_lines=False)
    table.add_column("ID", justify="right")
    table.add_column("Nombre")
    table.add_column("Email")
    table.add_column("Teléfono")
    table.add_column("Cliente")
    table.add_column("Proveedor")

    for c in contacts:
        table.add_row(
            str(c.id or ""),
            c.full_name,
            c.email or "",
            c.phone or "",
            "S" if c.is_customer else "N",
            "S" if c.is_supplier else "N",
        )
    console.print(table)


def show_contact(contact: ContactDTO) -> None:
    table = Table(show_header=False)
    table.add_row("ID", str(contact.id or ""))
    table.add_row("Nombre", contact.full_name)
    table.add_row("Email", contact.email or "")
    table.add_row("Teléfono", contact.phone or "")
    table.add_row("Empresa", contact.company or "")
    table.add_row("Notas", contact.notes or "")
    table.add_row("Cliente", "S" if contact.is_customer else "N")
    table.add_row("Proveedor", "S" if contact.is_supplier else "N")
    console.print(table)
