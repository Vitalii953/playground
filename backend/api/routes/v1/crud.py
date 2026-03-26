from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.players import Item
from app.schemas.schemas import ItemBase, ItemResponse


async def create_item(item: ItemBase, db: AsyncSession) -> ItemResponse:
    