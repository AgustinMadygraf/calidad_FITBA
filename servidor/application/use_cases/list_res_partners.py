from domain.repositories.res_partner_repository import IResPartnerRepository
from application.dtos.res_partner_dto import ResPartnerDTO
from application.use_cases._mappers import to_partner_dto


class ListResPartners:
    def __init__(self, repo: IResPartnerRepository) -> None:
        self.repo = repo

    def execute(self, limit: int, offset: int) -> list[ResPartnerDTO]:
        partners = self.repo.list(limit=limit, offset=offset)
        return [to_partner_dto(p) for p in partners]
