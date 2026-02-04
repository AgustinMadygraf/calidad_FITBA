from dataclasses import dataclass
from domain.exceptions import ValidationError
from domain.value_objects.email import Email
from domain.value_objects.phone import OptionalPhone


@dataclass
class Contact:
    full_name: str
    email: Email | None = None
    phone: OptionalPhone | None = None
    company: str | None = None
    notes: str | None = None
    is_customer: bool = False
    is_supplier: bool = False
    id: int | None = None

    def __post_init__(self) -> None:
        name = self.full_name.strip() if self.full_name else ""
        if not name:
            raise ValidationError("Nombre completo requerido")
        if len(name) > 120:
            raise ValidationError("Nombre demasiado largo")
        self.full_name = name

        if self.company is not None:
            company = self.company.strip()
            if company and len(company) > 120:
                raise ValidationError("Empresa demasiado larga")
            self.company = company if company else None

        if self.notes is not None:
            self.notes = self.notes.strip() if self.notes.strip() else None

        if self.email is not None and not isinstance(self.email, Email):
            raise ValidationError("Email inválido")
        if self.phone is not None and not isinstance(self.phone, OptionalPhone):
            raise ValidationError("Teléfono inválido")
