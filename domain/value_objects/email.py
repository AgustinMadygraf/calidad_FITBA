from dataclasses import dataclass
import re
from domain.exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        v = self.value.strip()
        if not v:
            raise ValidationError("Email vacío")
        if len(v) > 254:
            raise ValidationError("Email demasiado largo")
        if not _EMAIL_RE.match(v):
            raise ValidationError("Email inválido")
        object.__setattr__(self, "value", v)
