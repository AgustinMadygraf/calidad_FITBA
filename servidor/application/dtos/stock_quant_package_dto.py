from dataclasses import dataclass


@dataclass(frozen=True)
class StockQuantPackageDTO:
    id: int
    name: str
    package_type_id: int
    shipping_weight: float
    picking_id: int
