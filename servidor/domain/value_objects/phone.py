from dataclasses import dataclass
import re
from domain.exceptions import ValidationError

_PHONE_RE = re.compile(r"^[0-9+()\-\s]{3,40}$")


@dataclass(frozen=True)
class OptionalPhone:
    value: str | None

    def __post_init__(self) -> None:
        if self.value is None:
            return
        v = self.value.strip()
        if not v:
            object.__setattr__(self, "value", None)
            return
        if len(v) > 40:
            raise ValidationError("Teléfono demasiado largo")
        if not _PHONE_RE.match(v):
            raise ValidationError("Teléfono inválido")
        object.__setattr__(self, "value", v)
