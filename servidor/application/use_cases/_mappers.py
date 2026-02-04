from domain.entities.contact import Contact
from application.dtos.contact_dto import ContactDTO


def to_dto(contact: Contact) -> ContactDTO:
    return ContactDTO(
        id=contact.id,
        full_name=contact.full_name,
        email=contact.email.value if contact.email else None,
        phone=contact.phone.value if contact.phone else None,
        company=contact.company,
        notes=contact.notes,
        is_customer=contact.is_customer,
        is_supplier=contact.is_supplier,
    )
