from pydantic import BaseModel, Field


class StockQuantPackageBase(BaseModel):
    name: str = Field(..., max_length=64)
    package_type_id: int = Field(..., gt=0)
    shipping_weight: float = Field(default=0.0, ge=0)
    picking_id: int = Field(..., gt=0)


class StockQuantPackageCreate(StockQuantPackageBase):
    pass


class StockQuantPackageUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    package_type_id: int | None = Field(default=None, gt=0)
    shipping_weight: float | None = Field(default=None, ge=0)
    picking_id: int | None = Field(default=None, gt=0)


class StockQuantPackageResponse(StockQuantPackageBase):
    id: int


class StockQuantPackageListResponse(BaseModel):
    items: list[StockQuantPackageResponse]
    limit: int
    offset: int
