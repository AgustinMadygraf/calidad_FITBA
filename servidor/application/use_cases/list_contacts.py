from domain.repositories.contact_repository import IContactRepository
from application.dtos.contact_dto import ContactDTO
from application.use_cases._mappers import to_dto


class ListContacts:
    def __init__(self, repo: IContactRepository) -> None:
        self.repo = repo

    def execute(self, limit: int = 10, offset: int = 0) -> list[ContactDTO]:
        results = self.repo.list(limit=limit, offset=offset)
        return [to_dto(c) for c in results]
