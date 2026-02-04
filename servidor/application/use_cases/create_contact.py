from domain.entities.contact import Contact
from domain.repositories.contact_repository import IContactRepository
from domain.value_objects.email import Email
from domain.value_objects.phone import OptionalPhone
from application.dtos.contact_dto import ContactDTO
from application.use_cases._mappers import to_dto


class CreateContact:
    def __init__(self, repo: IContactRepository) -> None:
        self.repo = repo

    def execute(
        self,
        full_name: str,
        email: str | None = None,
        phone: str | None = None,
        company: str | None = None,
        notes: str | None = None,
        is_customer: bool = False,
        is_supplier: bool = False,
    ) -> ContactDTO:
        email_vo = Email(email) if email else None
        phone_vo = OptionalPhone(phone) if phone is not None else None
        contact = Contact(
            full_name=full_name,
            email=email_vo,
            phone=phone_vo,
            company=company,
            notes=notes,
            is_customer=is_customer,
            is_supplier=is_supplier,
        )
        created = self.repo.create(contact)
        return to_dto(created)
