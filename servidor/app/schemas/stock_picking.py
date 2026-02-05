from pydantic import BaseModel, Field


class StockPickingBase(BaseModel):
    name: str = Field(..., max_length=64)
    partner_id: int = Field(..., gt=0)


class StockPickingCreate(StockPickingBase):
    pass


class StockPickingUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    partner_id: int | None = Field(default=None, gt=0)


class StockPickingResponse(StockPickingBase):
    id: int


class StockPickingListResponse(BaseModel):
    items: list[StockPickingResponse]
    limit: int
    offset: int
