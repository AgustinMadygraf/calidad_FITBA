from domain.repositories.res_partner_repository import IResPartnerRepository
from application.dtos.res_partner_dto import ResPartnerDTO
from application.use_cases._mappers import to_partner_dto
from application.exceptions import NotFoundError


class GetResPartnerById:
    def __init__(self, repo: IResPartnerRepository) -> None:
        self.repo = repo

    def execute(self, partner_id: int) -> ResPartnerDTO:
        partner = self.repo.get_by_id(partner_id)
        if not partner:
            raise NotFoundError("Partner no encontrado")
        return to_partner_dto(partner)
