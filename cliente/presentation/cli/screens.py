from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from cliente.dtos.res_partner_dto import ResPartnerDTO
from cliente.dtos.stock_picking_dto import StockPickingDTO
from cliente.dtos.stock_package_type_dto import StockPackageTypeDTO
from cliente.dtos.stock_quant_package_dto import StockQuantPackageDTO

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
    console.rule(f"[title]ODOO-LIKE[/title]  [dim]|[/dim]  [label]{title}[/label]")


def footer(text: str = "ESC=Cancelar  ENTER=Continuar") -> None:
    console.rule(f"[dim]{text}[/dim]")


def partners_table(partners: list[ResPartnerDTO]) -> None:
    table = Table(show_lines=False, header_style="label")
    table.add_column("ID", justify="right", style="field")
    table.add_column("NOMBRE", style="field")
    table.add_column("EMAIL", style="field")
    table.add_column("TEL", style="field")

    for p in partners:
        table.add_row(str(p.id), p.name, p.email or "", p.phone or "")
    console.print(table)


def show_partner(partner: ResPartnerDTO) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("01 ID", str(partner.id))
    table.add_row("02 NOMBRE", partner.name)
    table.add_row("03 EMAIL", partner.email or "")
    table.add_row("04 TEL", partner.phone or "")
    console.print(table)


def pickings_table(pickings: list[StockPickingDTO]) -> None:
    table = Table(show_lines=False, header_style="label")
    table.add_column("ID", justify="right", style="field")
    table.add_column("REF", style="field")
    table.add_column("PARTNER", style="field")

    for p in pickings:
        table.add_row(str(p.id), p.name, str(p.partner_id))
    console.print(table)


def show_picking(picking: StockPickingDTO) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("01 ID", str(picking.id))
    table.add_row("02 REF", picking.name)
    table.add_row("03 PARTNER", str(picking.partner_id))
    console.print(table)


def package_types_table(items: list[StockPackageTypeDTO]) -> None:
    table = Table(show_lines=False, header_style="label")
    table.add_column("ID", justify="right", style="field")
    table.add_column("NOMBRE", style="field")
    table.add_column("PESO", style="field")
    for item in items:
        table.add_row(str(item.id), item.name, str(item.weight))
    console.print(table)


def show_package_type(item: StockPackageTypeDTO) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("01 ID", str(item.id))
    table.add_row("02 NOMBRE", item.name)
    table.add_row("03 PESO", str(item.weight))
    console.print(table)


def packages_table(items: list[StockQuantPackageDTO]) -> None:
    table = Table(show_lines=False, header_style="label")
    table.add_column("ID", justify="right", style="field")
    table.add_column("REF", style="field")
    table.add_column("TIPO", style="field")
    table.add_column("PESO", style="field")
    table.add_column("PICKING", style="field")
    for item in items:
        table.add_row(
            str(item.id),
            item.name,
            str(item.package_type_id),
            str(item.shipping_weight),
            str(item.picking_id),
        )
    console.print(table)


def show_package(item: StockQuantPackageDTO) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("01 ID", str(item.id))
    table.add_row("02 REF", item.name)
    table.add_row("03 TIPO", str(item.package_type_id))
    table.add_row("04 PESO", str(item.shipping_weight))
    table.add_row("05 PICKING", str(item.picking_id))
    console.print(table)
