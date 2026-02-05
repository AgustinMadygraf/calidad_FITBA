from rich.console import Console
from cliente.infrastructure.api_client import ApiClient, ApiError
from cliente.presentation.cli.prompts import (
    clear_screen,
    prompt_text,
    prompt_int,
    confirm,
    EscapeError,
)
from cliente.presentation.cli.screens import (
    header,
    footer,
    partners_table,
    show_partner,
    pickings_table,
    show_picking,
    package_types_table,
    show_package_type,
    packages_table,
    show_package,
)

console = Console()


def main_menu(api: ApiClient) -> None:
    while True:
        try:
            clear_screen()
            header("MENU PRINCIPAL")
            console.print("[green] 1)[/green] Partners (res.partner)")
            console.print("[green] 2)[/green] Pickings (stock.picking)")
            console.print("[green] 3)[/green] Package Types (stock.package.type)")
            console.print("[green] 4)[/green] Packages (stock.quant.package)")
            console.print("[green] 0)[/green] Salir")
            footer("ESC=Cancelar  0=Salir")
            option = console.input("==> ").strip()
            if "\x1b" in option:
                console.print("[yellow]Cancelado[/yellow]")
                console.input("Enter para continuar...")
                continue

            if option == "1":
                partners_menu(api)
            elif option == "2":
                pickings_menu(api)
            elif option == "3":
                package_types_menu(api)
            elif option == "4":
                packages_menu(api)
            elif option == "0":
                break
            else:
                console.print("[red]Opcion invalida[/red]")
                console.input("Enter para continuar...")
        except KeyboardInterrupt:
            console.print("[yellow]Cancelado[/yellow]")
            console.input("Enter para continuar...")
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            console.input("Enter para continuar...")
        except Exception as exc:
            console.print(f"[red]Error inesperado: {exc}[/red]")
            console.input("Enter para continuar...")


def partners_menu(api: ApiClient) -> None:
    while True:
        try:
            clear_screen()
            header("RES.PARTNER")
            console.print("[green] 1)[/green] Alta")
            console.print("[green] 2)[/green] Modificar")
            console.print("[green] 3)[/green] Baja")
            console.print("[green] 4)[/green] Consultar por ID")
            console.print("[green] 5)[/green] Listar")
            console.print("[green] 0)[/green] Volver")
            footer("ESC=Cancelar  0=Volver")
            option = console.input("==> ").strip()
            if "\x1b" in option:
                break

            if option == "1":
                create_partner_flow(api)
            elif option == "2":
                update_partner_flow(api)
            elif option == "3":
                delete_partner_flow(api)
            elif option == "4":
                get_partner_flow(api)
            elif option == "5":
                list_partners_flow(api)
            elif option == "0":
                break
        except KeyboardInterrupt:
            break
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            console.input("Enter para continuar...")
        except Exception as exc:
            console.print(f"[red]Error inesperado: {exc}[/red]")
            console.input("Enter para continuar...")


def create_partner_flow(api: ApiClient) -> None:
    clear_screen()
    header("ALTA RES.PARTNER")
    try:
        name = prompt_text("01 NOMBRE", required=True) or ""
        email = prompt_text("02 EMAIL")
        phone = prompt_text("03 TELEFONO")
        dto = api.create_res_partner({"name": name, "email": email, "phone": phone})
        console.print("[green]Partner creado[/green]")
        show_partner(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def update_partner_flow(api: ApiClient) -> None:
    clear_screen()
    header("MODIFICAR RES.PARTNER")
    try:
        partner_id = prompt_int("01 ID", required=True)
        name = prompt_text("02 NOMBRE (vacio=mantener)")
        email = prompt_text("03 EMAIL (vacio=mantener, '-'=borrar)")
        phone = prompt_text("04 TELEFONO (vacio=mantener, '-'=borrar)")
        payload = {}
        if name is not None:
            payload["name"] = name
        if email is not None:
            payload["email"] = None if email.strip() == "-" else email
        if phone is not None:
            payload["phone"] = None if phone.strip() == "-" else phone
        dto = api.update_res_partner(partner_id, payload)
        console.print("[green]Partner actualizado[/green]")
        show_partner(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def delete_partner_flow(api: ApiClient) -> None:
    clear_screen()
    header("BAJA RES.PARTNER")
    try:
        partner_id = prompt_int("01 ID", required=True)
        if not confirm("02 CONFIRMA ELIMINAR"):
            console.print("Cancelado")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        api.delete_res_partner(partner_id)
        console.print("[green]Partner eliminado[/green]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def get_partner_flow(api: ApiClient) -> None:
    clear_screen()
    header("CONSULTAR RES.PARTNER")
    try:
        partner_id = prompt_int("01 ID", required=True)
        dto = api.get_res_partner(partner_id)
        show_partner(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def list_partners_flow(api: ApiClient) -> None:
    clear_screen()
    header("LISTAR RES.PARTNER")
    limit = 10
    offset = 0
    while True:
        try:
            results = api.list_res_partners(limit=limit, offset=offset)
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        clear_screen()
        header(f"LISTAR RES.PARTNER  OFFSET {offset}")
        if results:
            partners_table(results)
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


def pickings_menu(api: ApiClient) -> None:
    while True:
        try:
            clear_screen()
            header("STOCK.PICKING")
            console.print("[green] 1)[/green] Alta")
            console.print("[green] 2)[/green] Modificar")
            console.print("[green] 3)[/green] Baja")
            console.print("[green] 4)[/green] Consultar por ID")
            console.print("[green] 5)[/green] Listar")
            console.print("[green] 0)[/green] Volver")
            footer("ESC=Cancelar  0=Volver")
            option = console.input("==> ").strip()
            if "\x1b" in option:
                break

            if option == "1":
                create_picking_flow(api)
            elif option == "2":
                update_picking_flow(api)
            elif option == "3":
                delete_picking_flow(api)
            elif option == "4":
                get_picking_flow(api)
            elif option == "5":
                list_pickings_flow(api)
            elif option == "0":
                break
        except KeyboardInterrupt:
            break
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            console.input("Enter para continuar...")
        except Exception as exc:
            console.print(f"[red]Error inesperado: {exc}[/red]")
            console.input("Enter para continuar...")


def create_picking_flow(api: ApiClient) -> None:
    clear_screen()
    header("ALTA STOCK.PICKING")
    try:
        name = prompt_text("01 REFERENCIA", required=True) or ""
        partner_id = prompt_int("02 PARTNER_ID", required=True)
        dto = api.create_stock_picking({"name": name, "partner_id": partner_id})
        console.print("[green]Picking creado[/green]")
        show_picking(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def update_picking_flow(api: ApiClient) -> None:
    clear_screen()
    header("MODIFICAR STOCK.PICKING")
    try:
        picking_id = prompt_int("01 ID", required=True)
        name = prompt_text("02 REFERENCIA (vacio=mantener)")
        partner_id = prompt_text("03 PARTNER_ID (vacio=mantener)")
        payload = {}
        if name is not None:
            payload["name"] = name
        if partner_id is not None and partner_id != "":
            payload["partner_id"] = int(partner_id)
        dto = api.update_stock_picking(picking_id, payload)
        console.print("[green]Picking actualizado[/green]")
        show_picking(dto)
    except ValueError:
        console.print("[red]partner_id invalido[/red]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def delete_picking_flow(api: ApiClient) -> None:
    clear_screen()
    header("BAJA STOCK.PICKING")
    try:
        picking_id = prompt_int("01 ID", required=True)
        if not confirm("02 CONFIRMA ELIMINAR"):
            console.print("Cancelado")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        api.delete_stock_picking(picking_id)
        console.print("[green]Picking eliminado[/green]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def get_picking_flow(api: ApiClient) -> None:
    clear_screen()
    header("CONSULTAR STOCK.PICKING")
    try:
        picking_id = prompt_int("01 ID", required=True)
        dto = api.get_stock_picking(picking_id)
        show_picking(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def list_pickings_flow(api: ApiClient) -> None:
    clear_screen()
    header("LISTAR STOCK.PICKING")
    limit = 10
    offset = 0
    while True:
        try:
            results = api.list_stock_pickings(limit=limit, offset=offset)
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        clear_screen()
        header(f"LISTAR STOCK.PICKING  OFFSET {offset}")
        if results:
            pickings_table(results)
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


def package_types_menu(api: ApiClient) -> None:
    while True:
        try:
            clear_screen()
            header("STOCK.PACKAGE.TYPE")
            console.print("[green] 1)[/green] Alta")
            console.print("[green] 2)[/green] Modificar")
            console.print("[green] 3)[/green] Baja")
            console.print("[green] 4)[/green] Consultar por ID")
            console.print("[green] 5)[/green] Listar")
            console.print("[green] 0)[/green] Volver")
            footer("ESC=Cancelar  0=Volver")
            option = console.input("==> ").strip()
            if "\x1b" in option:
                break

            if option == "1":
                create_package_type_flow(api)
            elif option == "2":
                update_package_type_flow(api)
            elif option == "3":
                delete_package_type_flow(api)
            elif option == "4":
                get_package_type_flow(api)
            elif option == "5":
                list_package_types_flow(api)
            elif option == "0":
                break
        except KeyboardInterrupt:
            break
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            console.input("Enter para continuar...")
        except Exception as exc:
            console.print(f"[red]Error inesperado: {exc}[/red]")
            console.input("Enter para continuar...")


def create_package_type_flow(api: ApiClient) -> None:
    clear_screen()
    header("ALTA STOCK.PACKAGE.TYPE")
    try:
        name = prompt_text("01 NOMBRE", required=True) or ""
        weight = prompt_text("02 PESO (tara, vacio=0)")
        payload = {"name": name, "weight": float(weight) if weight else 0.0}
        dto = api.create_stock_package_type(payload)
        console.print("[green]Tipo de paquete creado[/green]")
        show_package_type(dto)
    except ValueError:
        console.print("[red]Peso invalido[/red]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def update_package_type_flow(api: ApiClient) -> None:
    clear_screen()
    header("MODIFICAR STOCK.PACKAGE.TYPE")
    try:
        package_type_id = prompt_int("01 ID", required=True)
        name = prompt_text("02 NOMBRE (vacio=mantener)")
        weight = prompt_text("03 PESO (vacio=mantener)")
        payload = {}
        if name is not None:
            payload["name"] = name
        if weight is not None and weight != "":
            payload["weight"] = float(weight)
        dto = api.update_stock_package_type(package_type_id, payload)
        console.print("[green]Tipo de paquete actualizado[/green]")
        show_package_type(dto)
    except ValueError:
        console.print("[red]Peso invalido[/red]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def delete_package_type_flow(api: ApiClient) -> None:
    clear_screen()
    header("BAJA STOCK.PACKAGE.TYPE")
    try:
        package_type_id = prompt_int("01 ID", required=True)
        if not confirm("02 CONFIRMA ELIMINAR"):
            console.print("Cancelado")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        api.delete_stock_package_type(package_type_id)
        console.print("[green]Tipo de paquete eliminado[/green]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def get_package_type_flow(api: ApiClient) -> None:
    clear_screen()
    header("CONSULTAR STOCK.PACKAGE.TYPE")
    try:
        package_type_id = prompt_int("01 ID", required=True)
        dto = api.get_stock_package_type(package_type_id)
        show_package_type(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def list_package_types_flow(api: ApiClient) -> None:
    clear_screen()
    header("LISTAR STOCK.PACKAGE.TYPE")
    limit = 10
    offset = 0
    while True:
        try:
            results = api.list_stock_package_types(limit=limit, offset=offset)
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        clear_screen()
        header(f"LISTAR STOCK.PACKAGE.TYPE  OFFSET {offset}")
        if results:
            package_types_table(results)
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


def packages_menu(api: ApiClient) -> None:
    while True:
        try:
            clear_screen()
            header("STOCK.QUANT.PACKAGE")
            console.print("[green] 1)[/green] Alta")
            console.print("[green] 2)[/green] Modificar")
            console.print("[green] 3)[/green] Baja")
            console.print("[green] 4)[/green] Consultar por ID")
            console.print("[green] 5)[/green] Listar")
            console.print("[green] 0)[/green] Volver")
            footer("ESC=Cancelar  0=Volver")
            option = console.input("==> ").strip()
            if "\x1b" in option:
                break

            if option == "1":
                create_package_flow(api)
            elif option == "2":
                update_package_flow(api)
            elif option == "3":
                delete_package_flow(api)
            elif option == "4":
                get_package_flow(api)
            elif option == "5":
                list_packages_flow(api)
            elif option == "0":
                break
        except KeyboardInterrupt:
            break
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            console.input("Enter para continuar...")
        except Exception as exc:
            console.print(f"[red]Error inesperado: {exc}[/red]")
            console.input("Enter para continuar...")


def create_package_flow(api: ApiClient) -> None:
    clear_screen()
    header("ALTA STOCK.QUANT.PACKAGE")
    try:
        name = prompt_text("01 REFERENCIA", required=True) or ""
        package_type_id = prompt_int("02 PACKAGE_TYPE_ID", required=True)
        shipping_weight = prompt_text("03 PESO TOTAL (vacio=0)")
        picking_id = prompt_int("04 PICKING_ID", required=True)
        payload = {
            "name": name,
            "package_type_id": package_type_id,
            "shipping_weight": float(shipping_weight) if shipping_weight else 0.0,
            "picking_id": picking_id,
        }
        dto = api.create_stock_quant_package(payload)
        console.print("[green]Paquete creado[/green]")
        show_package(dto)
    except ValueError:
        console.print("[red]Peso invalido[/red]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def update_package_flow(api: ApiClient) -> None:
    clear_screen()
    header("MODIFICAR STOCK.QUANT.PACKAGE")
    try:
        package_id = prompt_int("01 ID", required=True)
        name = prompt_text("02 REFERENCIA (vacio=mantener)")
        package_type_id = prompt_text("03 PACKAGE_TYPE_ID (vacio=mantener)")
        shipping_weight = prompt_text("04 PESO TOTAL (vacio=mantener)")
        picking_id = prompt_text("05 PICKING_ID (vacio=mantener)")
        payload = {}
        if name is not None:
            payload["name"] = name
        if package_type_id is not None and package_type_id != "":
            payload["package_type_id"] = int(package_type_id)
        if shipping_weight is not None and shipping_weight != "":
            payload["shipping_weight"] = float(shipping_weight)
        if picking_id is not None and picking_id != "":
            payload["picking_id"] = int(picking_id)
        dto = api.update_stock_quant_package(package_id, payload)
        console.print("[green]Paquete actualizado[/green]")
        show_package(dto)
    except ValueError:
        console.print("[red]Dato invalido[/red]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def delete_package_flow(api: ApiClient) -> None:
    clear_screen()
    header("BAJA STOCK.QUANT.PACKAGE")
    try:
        package_id = prompt_int("01 ID", required=True)
        if not confirm("02 CONFIRMA ELIMINAR"):
            console.print("Cancelado")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        api.delete_stock_quant_package(package_id)
        console.print("[green]Paquete eliminado[/green]")
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def get_package_flow(api: ApiClient) -> None:
    clear_screen()
    header("CONSULTAR STOCK.QUANT.PACKAGE")
    try:
        package_id = prompt_int("01 ID", required=True)
        dto = api.get_stock_quant_package(package_id)
        show_package(dto)
    except ApiError as exc:
        console.print(f"[red]{exc.detail}[/red]")
    except EscapeError:
        console.print("[yellow]Cancelado[/yellow]")
    footer("ENTER=Continuar")
    console.input("==> ")


def list_packages_flow(api: ApiClient) -> None:
    clear_screen()
    header("LISTAR STOCK.QUANT.PACKAGE")
    limit = 10
    offset = 0
    while True:
        try:
            results = api.list_stock_quant_packages(limit=limit, offset=offset)
        except ApiError as exc:
            console.print(f"[red]{exc.detail}[/red]")
            footer("ENTER=Continuar")
            console.input("==> ")
            return
        clear_screen()
        header(f"LISTAR STOCK.QUANT.PACKAGE  OFFSET {offset}")
        if results:
            packages_table(results)
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
