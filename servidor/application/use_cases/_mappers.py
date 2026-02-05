from domain.entities.res_partner import ResPartner
from domain.entities.stock_picking import StockPicking
from domain.entities.stock_package_type import StockPackageType
from domain.entities.stock_quant_package import StockQuantPackage
from application.dtos.res_partner_dto import ResPartnerDTO
from application.dtos.stock_picking_dto import StockPickingDTO
from application.dtos.stock_package_type_dto import StockPackageTypeDTO
from application.dtos.stock_quant_package_dto import StockQuantPackageDTO


def to_partner_dto(partner: ResPartner) -> ResPartnerDTO:
    return ResPartnerDTO(
        id=partner.id,
        name=partner.name,
        email=partner.email,
        phone=partner.phone,
    )


def to_picking_dto(picking: StockPicking) -> StockPickingDTO:
    return StockPickingDTO(
        id=picking.id,
        name=picking.name,
        partner_id=picking.partner_id,
    )


def to_package_type_dto(package_type: StockPackageType) -> StockPackageTypeDTO:
    return StockPackageTypeDTO(
        id=package_type.id,
        name=package_type.name,
        weight=package_type.weight,
    )


def to_quant_package_dto(package: StockQuantPackage) -> StockQuantPackageDTO:
    return StockQuantPackageDTO(
        id=package.id,
        name=package.name,
        package_type_id=package.package_type_id,
        shipping_weight=package.shipping_weight,
        picking_id=package.picking_id,
    )
