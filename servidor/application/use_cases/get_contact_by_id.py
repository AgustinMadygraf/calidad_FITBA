from domain.repositories.contact_repository import IContactRepository
from application.exceptions import NotFoundError
from application.dtos.contact_dto import ContactDTO
from application.use_cases._mappers import to_dto


class GetContactById:
    def __init__(self, repo: IContactRepository) -> None:
        self.repo = repo

    def execute(self, contact_id: int) -> ContactDTO:
        contact = self.repo.get_by_id(contact_id)
        if not contact:
            raise NotFoundError("Contacto no encontrado")
        return to_dto(contact)
