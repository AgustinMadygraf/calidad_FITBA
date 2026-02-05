from abc import ABC, abstractmethod
from domain.entities.res_partner import ResPartner


class IResPartnerRepository(ABC):
    @abstractmethod
    def create(self, partner: ResPartner) -> ResPartner: ...

    @abstractmethod
    def update(self, partner: ResPartner) -> ResPartner: ...

    @abstractmethod
    def delete(self, partner_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, partner_id: int) -> ResPartner | None: ...

    @abstractmethod
    def list(self, limit: int, offset: int) -> list[ResPartner]: ...
