from dataclasses import dataclass


@dataclass(frozen=True)
class StockPickingDTO:
    id: int
    name: str
    partner_id: int
