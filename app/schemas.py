from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # allow parsing from ORM objects