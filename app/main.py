from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import aio_pika
from app.config import settings

# 1. Database Setup (Async)
DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# 2. RabbitMQ Connection Placeholder
RABBITMQ_URL = settings.RABBITMQ_URL

# Dependency to get DB session
async def get_db():
    async with async_session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to RabbitMQ
    app.state.mq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
    app.state.mq_channel = await app.state.mq_connection.channel()
    print("Connected to RabbitMQ and Database")

    yield

    # Shutdown: Clean up
    await app.state.mq_connection.close()
    await engine.dispose()
    print("Shutdown complete")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # Simple query to verify DB is alive
    from sqlalchemy import text

    await db.execute(text("SELECT 1"))
    return {"status": "online", "database": "connected"}
