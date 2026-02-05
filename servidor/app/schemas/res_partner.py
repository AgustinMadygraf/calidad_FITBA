from pydantic import BaseModel, Field


class ResPartnerBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)


class ResPartnerCreate(ResPartnerBase):
    pass


class ResPartnerUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)


class ResPartnerResponse(ResPartnerBase):
    id: int


class ResPartnerListResponse(BaseModel):
    items: list[ResPartnerResponse]
    limit: int
    offset: int
