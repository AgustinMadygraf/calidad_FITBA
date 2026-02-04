from dataclasses import dataclass


@dataclass(frozen=True)
class ContactDTO:
    id: int
    full_name: str
    email: str | None
    phone: str | None
    company: str | None
    notes: str | None
    is_customer: bool
    is_supplier: bool
