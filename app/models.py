from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[Annotated[int, mapped_column(primary_key=True, autoincrement=True)]] 
    name: Mapped[Annotated[str, mapped_column(String(100), nullable=False)]]
    description: Mapped[Annotated[str | None, mapped_column(String(255), nullable=True)]]
    price: Mapped[Annotated[float, mapped_column(nullable=False)]]
    tax: Mapped[Annotated[float | None, mapped_column(nullable=True)]]
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]]  