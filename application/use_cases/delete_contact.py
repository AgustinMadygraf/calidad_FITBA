from domain.repositories.contact_repository import IContactRepository
from application.exceptions import NotFoundError


class DeleteContact:
    def __init__(self, repo: IContactRepository) -> None:
        self.repo = repo

    def execute(self, contact_id: int) -> None:
        existing = self.repo.get_by_id(contact_id)
        if not existing:
            raise NotFoundError("Contacto no encontrado")
        self.repo.delete(contact_id)
