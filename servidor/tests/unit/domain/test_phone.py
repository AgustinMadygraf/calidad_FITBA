import pytest
from domain.value_objects.phone import OptionalPhone
from domain.exceptions import ValidationError


def test_optional_phone_none_and_empty():
    assert OptionalPhone(None).value is None
    assert OptionalPhone("  ").value is None


def test_optional_phone_valid():
    assert OptionalPhone("+54 11 1234").value == "+54 11 1234"


def test_optional_phone_invalid():
    with pytest.raises(ValidationError):
        OptionalPhone("abc123")
