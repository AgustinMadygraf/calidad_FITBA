import pytest
from domain.entities.contact import Contact
from domain.exceptions import ValidationError
from domain.value_objects.email import Email
from domain.value_objects.phone import OptionalPhone


def test_contact_requires_name():
    with pytest.raises(ValidationError):
        Contact(full_name="")


def test_contact_accepts_email_and_phone():
    c = Contact(full_name="Juan Perez", email=Email("a@b.com"), phone=OptionalPhone("+54 11 1234"))
    assert c.full_name == "Juan Perez"
