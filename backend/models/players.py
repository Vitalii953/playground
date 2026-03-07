from typing import Annotated
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    id: Mapped[Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]] 
    created_at: Mapped[Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]]  
    last_updated: Mapped[Annotated[datetime, mapped_column(onupdate=func.now(), server_default=func.now())]]

    gold: Mapped[Annotated[int, mapped_column(default=0)]]
    keys: Mapped[Annotated[int, mapped_column(default=0)]]
    current_floor: Mapped[Annotated[int, mapped_column(default=0)]]  # everyone starts at 0

    preferences: Mapped[Annotated[dict, mapped_column(JSONB, default=dict)]]