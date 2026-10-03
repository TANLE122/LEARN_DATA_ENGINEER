from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(ge=0)


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ItemQuery(BaseModel):
    """Used as query params for GET /items and as JSON body for POST /items/search."""

    name: str | None = Field(None, description="Case-insensitive substring match")
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    sort_by: Literal["id", "name", "price", "created_at"] = "id"
    sort_order: Literal["asc", "desc"] = "asc"
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
