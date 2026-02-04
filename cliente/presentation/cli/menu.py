from rich.console import Console
from cliente.infrastructure.api_client import ApiClient, ApiError
from cliente.presentation.cli.prompts import (
    clear_screen,
    prompt_text,
    prompt_int,
    prompt_bool,
    confirm,
    EscapeError,
)
from cliente.presentation.cli.screens import header, footer, contacts_table, show_contact

console = Console()


def main_menu(api: ApiClient) -> None:
    while True:
        clear_screen()
        header("MENÚ PRINCIPAL")
        console.print("[green] 1)[/green] Alta contacto")
        console.print("[green] 2)[/green] Modificar contacto")
        console.print("[green] 3)[/green] Baja contacto")
        console.print("[green] 4)[/green] Consultar por ID")
        console.print("[green] 5)[/green] Buscar")
        console.print("[green] 6)[/green] Listar")
        console.print("[green] 0)[/green] Salir")
        footer("ESC=Cancelar  0=Salir")
        try:
            option = console.input("==> ").strip()
            if "\x1b" in option:
                console.print("[yellow]Cancelado[/yellow]")
                console.input("Enter para continuar...")
                continue
        except KeyboardInterrupt:
            console.print("[yellow]Cancelado[/yellow]")
            console.input("Enter para continuar...")
            continue

        if option == "1":
            create_contact_flow(api)
        elif option == "2":
            update_contact_flow(api)
        elif option == "3":
            delete_contact_flow(api)
        elif option == "4":
            get_contact_flow(api)
        elif option == "5":
            search_contacts_flow(api)
        elif option == "6":
            list_contacts_flow(api)
        elif option == "0":
            break
        else:
            console.print("[red]Opción inválida[/red]")
            console.input("Enter para continuar...")


def create_contact_flow(api: ApiClient) -> None:
    clear_screen()
    header("ALTA CONTACTO")
    try:
        full_name = prompt_text("01 NOMBRE COMPLETO", required=True) or ""
        email = prompt_text("02 EMAIL")
        phone = prompt_text("03 TELÉFONO")
        company = prompt_text("04 EMPRESA")
        notes = prompt_text("05 NOTAS")
        is_customer = prompt_bool("06 ES CLIENTE", default=False)
        is_supplier = prompt_bool("07 ES PROVEEDOR", default=False)

        dto = api.create_contact(
            {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "company": company,
                "notes": notes,
                "is_customer": is_customer,
                "is_supplier": is_supplier,
            }
        )
        console.print("[green]Contacto creado[/green]")
        show_contact(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def update_contact_flow(api: ApiClient) -> None:
    clear_screen()
    header("MODIFICAR CONTACTO")
    try:
        contact_id = prompt_int("01 ID", required=True)
        full_name = prompt_text("02 NOMBRE (vacío=mantener)")
        email = prompt_text("03 EMAIL (vacío=mantener, '-'=borrar)")
        phone = prompt_text("04 TELÉFONO (vacío=mantener, '-'=borrar)")
        company = prompt_text("05 EMPRESA (vacío=mantener, '-'=borrar)")
        notes = prompt_text("06 NOTAS (vacío=mantener, '-'=borrar)")
        is_customer = prompt_text("07 ES CLIENTE (S/N, vacío=mantener)")
        is_supplier = prompt_text("08 ES PROVEEDOR (S/N, vacío=mantener)")

        def parse_bool(text: str | None) -> bool | None:
            if text is None or text == "":
                return None
            v = text.strip().lower()
            if v in ("s", "si", "sí", "y", "yes"):
                return True
            if v in ("n", "no"):
                return False
            raise ValueError("Valor booleano inválido")

        payload = {}
        if full_name is not None:
            payload["full_name"] = full_name
        if email is not None:
            payload["email"] = None if email.strip() == "-" else email
        if phone is not None:
            payload["phone"] = None if phone.strip() == "-" else phone
        if company is not None:
            payload["company"] = None if company.strip() == "-" else company
        if notes is not None:
            payload["notes"] = None if notes.strip() == "-" else notes
        if is_customer is not None:
            payload["is_customer"] = parse_bool(is_customer)
        if is_supplier is not None:
            payload["is_supplier"] = parse_bool(is_supplier)

        dto = api.update_contact(contact_id, payload)
        console.print("[green]Contacto actualizado[/green]")
        show_contact(dto)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def delete_contact_flow(api: ApiClient) -> None:
    clear_screen()
    header("BAJA CONTACTO")
    try:
        contact_id = prompt_int("01 ID", required=True)
        if not confirm("02 CONFIRMA ELIMINAR"):
            console.print("Cancelado")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        api.delete_contact(contact_id)
        console.print("[green]Contacto eliminado[/green]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def get_contact_flow(api: ApiClient) -> None:
    clear_screen()
    header("CONSULTAR POR ID")
    try:
        contact_id = prompt_int("01 ID", required=True)
        dto = api.get_contact(contact_id)
        show_contact(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def search_contacts_flow(api: ApiClient) -> None:
    clear_screen()
    header("BUSCAR")
    try:
        query = prompt_text("01 TEXTO", required=True) or ""
        results = api.search_contacts(query=query, limit=50, offset=0)
        if results:
            contacts_table(results)
        else:
            console.print("[yellow]Sin resultados[/yellow]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def list_contacts_flow(api: ApiClient) -> None:
    clear_screen()
    header("LISTAR")
    limit = 10
    offset = 0
    while True:
        try:
            results = api.list_contacts(limit=limit, offset=offset)
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        clear_screen()
        header(f"LISTAR  OFFSET {offset}")
        if results:
            contacts_table(results)
        else:
            console.print("[yellow]Sin resultados[/yellow]")
        console.print("[green]N)[/green] siguiente   [green]P)[/green] anterior   [green]0)[/green] volver")
        footer("ESC=Cancelar")
        try:
            choice = console.input("==> ").strip().lower()
            if "\x1b" in choice:
                break
        except KeyboardInterrupt:
            break
        if choice == "n":
            offset += limit
        elif choice == "p":
            offset = max(0, offset - limit)
        elif choice == "0":
            break
