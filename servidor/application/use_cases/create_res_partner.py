from domain.entities.res_partner import ResPartner
from domain.repositories.res_partner_repository import IResPartnerRepository
from application.dtos.res_partner_dto import ResPartnerDTO
from application.use_cases._mappers import to_partner_dto


class CreateResPartner:
    def __init__(self, repo: IResPartnerRepository) -> None:
        self.repo = repo

    def execute(self, name: str, email: str | None = None, phone: str | None = None) -> ResPartnerDTO:
        partner = ResPartner(name=name, email=email, phone=phone)
        created = self.repo.create(partner)
        return to_partner_dto(created)
