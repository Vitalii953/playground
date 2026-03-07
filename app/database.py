from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings


# The engine is created once at import time; if you want to support runtime
# reconfiguration you could move this into a factory.
engine = create_async_engine(
    str(settings.database_url),
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    async with AsyncSessionLocal() as session:
        yield session