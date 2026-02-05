from dataclasses import dataclass
from domain.exceptions import ValidationError


@dataclass
class StockPicking:
    name: str
    partner_id: int
    id: int | None = None

    def __post_init__(self) -> None:
        name = self.name.strip() if self.name else ""
        if not name:
            raise ValidationError("Referencia requerida")
        if len(name) > 64:
            raise ValidationError("Referencia demasiado larga")
        self.name = name

        if self.partner_id is None or self.partner_id <= 0:
            raise ValidationError("partner_id requerido")
