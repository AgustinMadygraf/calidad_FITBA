from dataclasses import dataclass


@dataclass(frozen=True)
class StockPackageTypeDTO:
    id: int
    name: str
    weight: float
