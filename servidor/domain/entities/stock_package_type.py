from dataclasses import dataclass
from domain.exceptions import ValidationError


@dataclass
class StockPackageType:
    name: str
    weight: float = 0.0
    id: int | None = None

    def __post_init__(self) -> None:
        name = self.name.strip() if self.name else ""
        if not name:
            raise ValidationError("Nombre requerido")
        if len(name) > 64:
            raise ValidationError("Nombre demasiado largo")
        self.name = name

        if self.weight is None or self.weight < 0:
            raise ValidationError("Peso invalido")
