from domain.entities.res_partner import ResPartner
from domain.repositories.res_partner_repository import IResPartnerRepository
from application.dtos.res_partner_dto import ResPartnerDTO
from application.use_cases._mappers import to_partner_dto
from application.exceptions import NotFoundError


class UpdateResPartner:
    def __init__(self, repo: IResPartnerRepository) -> None:
        self.repo = repo

    def execute(
        self, partner_id: int, name: str | None = None, email: str | None = None, phone: str | None = None
    ) -> ResPartnerDTO:
        existing = self.repo.get_by_id(partner_id)
        if not existing:
            raise NotFoundError("Partner no encontrado")
        partner = ResPartner(
            id=partner_id,
            name=name if name is not None else existing.name,
            email=email if email is not None else existing.email,
            phone=phone if phone is not None else existing.phone,
        )
        updated = self.repo.update(partner)
        return to_partner_dto(updated)
