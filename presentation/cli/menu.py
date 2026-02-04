from typing import Callable
from rich.console import Console
from domain.exceptions import ValidationError
from application.exceptions import NotFoundError, DuplicateEmailError, DatabaseError
from application.ports.unit_of_work import IUnitOfWork
from application.use_cases.create_contact import CreateContact
from application.use_cases.update_contact import UpdateContact
from application.use_cases.delete_contact import DeleteContact
from application.use_cases.get_contact_by_id import GetContactById
from application.use_cases.search_contacts import SearchContacts
from application.use_cases.list_contacts import ListContacts
from presentation.cli.prompts import clear_screen, prompt_text, prompt_int, prompt_bool, confirm, EscapeError
from presentation.cli.screens import header, contacts_table, show_contact

console = Console()


def main_menu(uow_factory: Callable[[], IUnitOfWork]) -> None:
    while True:
        clear_screen()
        console.print("[bold]CRUD Contactos[/bold]")
        console.print("1) Alta contacto")
        console.print("2) Modificar contacto")
        console.print("3) Baja contacto")
        console.print("4) Consultar por ID")
        console.print("5) Buscar")
        console.print("6) Listar")
        console.print("0) Salir")
        try:
            option = console.input("Opción: ").strip()
            if "\x1b" in option:
                console.print("[yellow]Cancelado[/yellow]")
                console.input("Enter para continuar...")
                continue
        except KeyboardInterrupt:
            console.print("[yellow]Cancelado[/yellow]")
            console.input("Enter para continuar...")
            continue

        if option == "1":
            create_contact_flow(uow_factory)
        elif option == "2":
            update_contact_flow(uow_factory)
        elif option == "3":
            delete_contact_flow(uow_factory)
        elif option == "4":
            get_contact_flow(uow_factory)
        elif option == "5":
            search_contacts_flow(uow_factory)
        elif option == "6":
            list_contacts_flow(uow_factory)
        elif option == "0":
            break
        else:
            console.print("[red]Opción inválida[/red]")
            console.input("Enter para continuar...")


def create_contact_flow(uow_factory: Callable[[], IUnitOfWork]) -> None:
    clear_screen()
    header("Alta")
    try:
        full_name = prompt_text("Nombre completo", required=True) or ""
        email = prompt_text("Email")
        phone = prompt_text("Teléfono")
        company = prompt_text("Empresa")
        notes = prompt_text("Notas")
        is_customer = prompt_bool("Es cliente", default=False)
        is_supplier = prompt_bool("Es proveedor", default=False)

        with uow_factory() as uow:
            use_case = CreateContact(uow.contacts)
            dto = use_case.execute(
                full_name=full_name,
                email=email,
                phone=phone,
                company=company,
                notes=notes,
                is_customer=is_customer,
                is_supplier=is_supplier,
            )
        console.print("[green]Contacto creado[/green]")
        show_contact(dto)
    except (ValidationError, DuplicateEmailError, DatabaseError) as exc:
        console.print(f"[red]{exc}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    console.input("Enter para continuar...")


def update_contact_flow(uow_factory: Callable[[], IUnitOfWork]) -> None:
    clear_screen()
    header("Modificar")
    try:
        contact_id = prompt_int("ID", required=True)
        full_name = prompt_text("Nombre completo (vacío para mantener)")
        email = prompt_text("Email (vacío para mantener, '-' para borrar)")
        phone = prompt_text("Teléfono (vacío para mantener, '-' para borrar)")
        company = prompt_text("Empresa (vacío para mantener, '-' para borrar)")
        notes = prompt_text("Notas (vacío para mantener, '-' para borrar)")
        is_customer = prompt_text("Es cliente (S/N, vacío para mantener)")
        is_supplier = prompt_text("Es proveedor (S/N, vacío para mantener)")

        def parse_bool(text: str | None) -> bool | None:
            if text is None or text == "":
                return None
            v = text.strip().lower()
            if v in ("s", "si", "sí", "y", "yes"):
                return True
            if v in ("n", "no"):
                return False
            raise ValidationError("Valor booleano inválido")

        def normalize_optional(text: str | None) -> str | None:
            if text is None:
                return None
            if text.strip() == "-":
                return ""
            return text

        with uow_factory() as uow:
            use_case = UpdateContact(uow.contacts)
            dto = use_case.execute(
                contact_id=contact_id,
                full_name=full_name,
                email=normalize_optional(email),
                phone=normalize_optional(phone),
                company=normalize_optional(company),
                notes=normalize_optional(notes),
                is_customer=parse_bool(is_customer),
                is_supplier=parse_bool(is_supplier),
            )
        console.print("[green]Contacto actualizado[/green]")
        show_contact(dto)
    except (ValidationError, NotFoundError, DuplicateEmailError, DatabaseError) as exc:
        console.print(f"[red]{exc}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    console.input("Enter para continuar...")


def delete_contact_flow(uow_factory: Callable[[], IUnitOfWork]) -> None:
    clear_screen()
    header("Baja")
    try:
        contact_id = prompt_int("ID", required=True)
        if not confirm("Confirma eliminar"):
            console.print("Cancelado")
            console.input("Enter para continuar...")
            return
        with uow_factory() as uow:
            use_case = DeleteContact(uow.contacts)
            use_case.execute(contact_id)
        console.print("[green]Contacto eliminado[/green]")
    except (NotFoundError, DatabaseError) as exc:
        console.print(f"[red]{exc}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    console.input("Enter para continuar...")


def get_contact_flow(uow_factory: Callable[[], IUnitOfWork]) -> None:
    clear_screen()
    header("Consultar por ID")
    try:
        contact_id = prompt_int("ID", required=True)
        with uow_factory() as uow:
            use_case = GetContactById(uow.contacts)
            dto = use_case.execute(contact_id)
        show_contact(dto)
    except (NotFoundError, DatabaseError) as exc:
        console.print(f"[red]{exc}[/red]")
    except DatabaseError as exc:
        console.print(f"[red]{exc}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    console.input("Enter para continuar...")


def search_contacts_flow(uow_factory: Callable[[], IUnitOfWork]) -> None:
    clear_screen()
    header("Buscar")
    try:
        query = prompt_text("Buscar", required=True) or ""
        with uow_factory() as uow:
            use_case = SearchContacts(uow.contacts)
            results = use_case.execute(query=query, limit=50, offset=0)
        if results:
            contacts_table(results)
        else:
            console.print("[yellow]Sin resultados[/yellow]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    console.input("Enter para continuar...")


def list_contacts_flow(uow_factory: Callable[[], IUnitOfWork]) -> None:
    clear_screen()
    header("Listar")
    limit = 10
    offset = 0
    while True:
        try:
            with uow_factory() as uow:
                use_case = ListContacts(uow.contacts)
                results = use_case.execute(limit=limit, offset=offset)
        except DatabaseError as exc:
            console.print(f"[red]{exc}[/red]")
            console.input("Enter para continuar...")
            return
        clear_screen()
        header(f"Listar (offset {offset})")
        if results:
            contacts_table(results)
        else:
            console.print("[yellow]Sin resultados[/yellow]")
        console.print("n) siguiente  p) anterior  0) volver")
        try:
            choice = console.input("Opción: ").strip().lower()
        except KeyboardInterrupt:
            break
        if choice == "n":
            offset += limit
        elif choice == "p":
            offset = max(0, offset - limit)
        elif choice == "0":
            break
