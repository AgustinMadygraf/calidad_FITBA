from dataclasses import dataclass
from domain.exceptions import ValidationError


@dataclass
class ResPartner:
    name: str
    email: str | None = None
    phone: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        name = self.name.strip() if self.name else ""
        if not name:
            raise ValidationError("Nombre requerido")
        if len(name) > 255:
            raise ValidationError("Nombre demasiado largo")
        self.name = name

        if self.email is not None:
            email = self.email.strip()
            if not email:
                self.email = None
            elif len(email) > 254:
                raise ValidationError("Email demasiado largo")
            else:
                self.email = email

        if self.phone is not None:
            phone = self.phone.strip()
            if not phone:
                self.phone = None
            elif len(phone) > 40:
                raise ValidationError("Telefono demasiado largo")
            else:
                self.phone = phone
