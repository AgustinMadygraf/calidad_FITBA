import pytest
from domain.entities.res_partner import ResPartner
from domain.entities.stock_package_type import StockPackageType
from domain.entities.stock_quant_package import StockQuantPackage
from domain.entities.stock_picking import StockPicking
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


def test_stock_quant_package_negative_weight():
    with pytest.raises(ValidationError):
        StockQuantPackage(name="PACK002", package_type_id=1, picking_id=1, shipping_weight=-1)


def test_res_partner_optional_fields():
    partner = ResPartner(name="Cliente", email="  test@example.com ", phone=" +54 11 1234 ")
    assert partner.email == "test@example.com"
    assert partner.phone == "+54 11 1234"


def test_res_partner_empty_optional_fields():
    partner = ResPartner(name="Cliente", email="  ", phone="  ")
    assert partner.email is None
    assert partner.phone is None


def test_res_partner_phone_too_long():
    with pytest.raises(ValidationError):
        ResPartner(name="Cliente", phone="1" * 41)


def test_res_partner_name_too_long():
    with pytest.raises(ValidationError):
        ResPartner(name="a" * 256)


def test_stock_picking_name_too_long():
    with pytest.raises(ValidationError):
        StockPicking(name="x" * 65, partner_id=1)


def test_stock_package_type_name_too_long():
    with pytest.raises(ValidationError):
        StockPackageType(name="x" * 65, weight=1)


def test_stock_quant_package_name_too_long():
    with pytest.raises(ValidationError):
        StockQuantPackage(name="x" * 65, package_type_id=1, shipping_weight=1, picking_id=1)
