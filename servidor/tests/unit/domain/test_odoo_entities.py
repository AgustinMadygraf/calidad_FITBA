import pytest
from domain.entities.res_partner import ResPartner
from domain.entities.stock_package_type import StockPackageType
from domain.entities.stock_quant_package import StockQuantPackage
from domain.exceptions import ValidationError


def test_res_partner_requires_name():
    with pytest.raises(ValidationError):
        ResPartner(name="")


def test_stock_package_type_weight_non_negative():
    with pytest.raises(ValidationError):
        StockPackageType(name="Caja", weight=-1)


def test_stock_quant_package_requires_relations():
    with pytest.raises(ValidationError):
        StockQuantPackage(name="PACK001", package_type_id=0, picking_id=0, shipping_weight=1)
