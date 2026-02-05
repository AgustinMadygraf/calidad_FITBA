from domain.repositories.res_partner_repository import IResPartnerRepository
from application.exceptions import NotFoundError


class DeleteResPartner:
    def __init__(self, repo: IResPartnerRepository) -> None:
        self.repo = repo

    def execute(self, partner_id: int) -> None:
        existing = self.repo.get_by_id(partner_id)
        if not existing:
            raise NotFoundError("Partner no encontrado")
        self.repo.delete(partner_id)
