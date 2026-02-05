from pydantic import BaseModel, Field


class StockPackageTypeBase(BaseModel):
    name: str = Field(..., max_length=64)
    weight: float = Field(default=0.0, ge=0)


class StockPackageTypeCreate(StockPackageTypeBase):
    pass


class StockPackageTypeUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    weight: float | None = Field(default=None, ge=0)


class StockPackageTypeResponse(StockPackageTypeBase):
    id: int


class StockPackageTypeListResponse(BaseModel):
    items: list[StockPackageTypeResponse]
    limit: int
    offset: int
