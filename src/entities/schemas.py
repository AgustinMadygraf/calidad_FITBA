from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class TerminalExecuteRequest(BaseModel):
    session_id: str | None = None
    command: str
    args: dict[str, Any] = Field(default_factory=dict)


class TerminalExecuteResponse(BaseModel):
    session_id: str
    screen: str
    next_actions: list[str] = Field(default_factory=list)


class ProductBase(BaseModel):
    model_config = ConfigDict(extra="allow")
    external_id: str | None = None
    name: str
    sku: str | None = None
    price: float | None = None
    xubio_payload: dict[str, Any] | None = Field(default=None, exclude=True)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str | None = None
    sku: str | None = None
    price: float | None = None
    xubio_payload: dict[str, Any] | None = Field(default=None, exclude=True)


class ProductOut(ProductBase):
    external_id: str


class ProductList(BaseModel):
    items: list[ProductOut]

