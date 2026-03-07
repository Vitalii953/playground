from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Item
from app.schemas import ItemBase, ItemResponse


async def create_item(item: ItemBase, db: AsyncSession) -> ItemResponse:
    """
    For a bare‑bones application we simply construct the ORM object, add
    it, flush to get the primary key, and return the schema using
    ``model_validate``.
    """

    obj = Item(**item.model_dump())
    db.add(obj)
    await db.flush()  # populate ``obj.id``
    await db.refresh(obj)  # populate any other database defaults (e.g. ``created_at``)
    return ItemResponse.model_validate(obj)

async def get_items(offset: int, limit: int, db: AsyncSession) -> list[ItemResponse]:
    # simple list query; nothing fancy required yet
    stmt = select(Item).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return [ItemResponse.model_validate(obj) for obj in result.scalars().all()]
