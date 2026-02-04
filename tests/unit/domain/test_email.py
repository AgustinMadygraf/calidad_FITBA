import pytest
from domain.value_objects.email import Email
from domain.exceptions import ValidationError


def test_email_valid():
    email = Email("test@example.com")
    assert email.value == "test@example.com"


@pytest.mark.parametrize("value", ["", "no-at", "a@b", "a@b@c", "a b@c.com"])
def test_email_invalid(value: str):
    with pytest.raises(ValidationError):
        Email(value)
