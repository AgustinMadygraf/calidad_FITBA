from domain.entities.contact import Contact
from domain.repositories.contact_repository import IContactRepository
from domain.value_objects.email import Email
from domain.value_objects.phone import OptionalPhone
from application.dtos.contact_dto import ContactDTO
from application.exceptions import NotFoundError
from application.use_cases._mappers import to_dto


class UpdateContact:
    def __init__(self, repo: IContactRepository) -> None:
        self.repo = repo

    def execute(
        self,
        contact_id: int,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company: str | None = None,
        notes: str | None = None,
        is_customer: bool | None = None,
        is_supplier: bool | None = None,
    ) -> ContactDTO:
        existing = self.repo.get_by_id(contact_id)
        if not existing:
            raise NotFoundError("Contacto no encontrado")

        if email is None:
            new_email = existing.email
        elif email == "":
            new_email = None
        else:
            new_email = Email(email)

        if phone is None:
            new_phone = existing.phone
        elif phone == "":
            new_phone = OptionalPhone(None)
        else:
            new_phone = OptionalPhone(phone)

        updated = Contact(
            id=existing.id,
            full_name=full_name if full_name is not None else existing.full_name,
            email=new_email,
            phone=new_phone,
            company=company if company is not None else existing.company,
            notes=notes if notes is not None else existing.notes,
            is_customer=is_customer if is_customer is not None else existing.is_customer,
            is_supplier=is_supplier if is_supplier is not None else existing.is_supplier,
        )
        updated = self.repo.update(updated)
        return to_dto(updated)
