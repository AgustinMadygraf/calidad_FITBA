from dataclasses import dataclass


@dataclass(frozen=True)
class ResPartnerDTO:
    id: int
    name: str
    email: str | None
    phone: str | None
