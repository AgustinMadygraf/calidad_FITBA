from dataclasses import dataclass
from domain.exceptions import ValidationError


@dataclass
class StockQuantPackage:
    name: str
    package_type_id: int
    shipping_weight: float = 0.0
    picking_id: int = 0
    id: int | None = None

    def __post_init__(self) -> None:
        name = self.name.strip() if self.name else ""
        if not name:
            raise ValidationError("Referencia requerida")
        if len(name) > 64:
            raise ValidationError("Referencia demasiado larga")
        self.name = name

        if self.package_type_id is None or self.package_type_id <= 0:
            raise ValidationError("package_type_id requerido")
        if self.picking_id is None or self.picking_id <= 0:
            raise ValidationError("picking_id requerido")
        if self.shipping_weight is None or self.shipping_weight < 0:
            raise ValidationError("Peso invalido")
