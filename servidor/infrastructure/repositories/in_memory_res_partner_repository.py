from domain.entities.res_partner import ResPartner
from domain.repositories.res_partner_repository import IResPartnerRepository


class InMemoryResPartnerRepository(IResPartnerRepository):
    def __init__(self) -> None:
        self._items: dict[int, ResPartner] = {}
        self._next_id = 1

    def create(self, partner: ResPartner) -> ResPartner:
        partner.id = self._next_id
        self._next_id += 1
        self._items[partner.id] = partner
        return partner

    def update(self, partner: ResPartner) -> ResPartner:
        self._items[partner.id] = partner
        return partner

    def delete(self, partner_id: int) -> None:
        self._items.pop(partner_id, None)

    def get_by_id(self, partner_id: int) -> ResPartner | None:
        return self._items.get(partner_id)

    def list(self, limit: int, offset: int) -> list[ResPartner]:
        items = list(self._items.values())
        return items[offset : offset + limit]
