from pydantic import BaseModel, Field


class ContactBase(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    company: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    is_customer: bool | None = None
    is_supplier: bool | None = None


class ContactCreate(ContactBase):
    full_name: str


class ContactUpdate(ContactBase):
    pass


class ContactResponse(BaseModel):
    id: int
    full_name: str
    email: str | None
    phone: str | None
    company: str | None
    notes: str | None
    is_customer: bool
    is_supplier: bool


class ContactListResponse(BaseModel):
    items: list[ContactResponse]
    limit: int
    offset: int
