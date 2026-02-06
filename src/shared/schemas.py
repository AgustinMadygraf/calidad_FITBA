from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class TerminalExecuteRequest(BaseModel):
    session_id: str | None = None
    command: str
    args: dict[str, Any] = Field(default_factory=dict)


class TerminalExecuteResponse(BaseModel):
    session_id: str
    screen: str
    next_actions: list[str] = Field(default_factory=list)


class ProductBase(BaseModel):
    external_id: str | None = None
    name: str
    sku: str | None = None
    price: float | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    price: float | None = None


class ProductOut(ProductBase):
    external_id: str


class ProductList(BaseModel):
    items: list[ProductOut]


class IntegrationRecordOut(BaseModel):
    id: int
    entity_type: str
    operation: str
    external_id: str | None
    payload_json: dict[str, Any]
    status: Literal["local", "synced", "error"]
    last_error: str | None
