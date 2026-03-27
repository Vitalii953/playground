import asyncio
import logging
from contextlib import asynccontextmanager
from game_internals.core.schemas.game_settings import languages
import aio_pika
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import engine, get_db
from backend.core.redis import get_redis
from backend.services.translator.translation_service import translate
from backend.services.auto_save import auto_save_stale_sessions
from backend.api.routes.v1 import game

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("App startup")

    # RabbitMQ may not be ready the instant this container starts.
    # Retry a few times before failing hard.
    attempts = 0
    while attempts < 10:
        try:
            app.state.mq_connection = await aio_pika.connect_robust(
                str(settings.rabbitmq_url)
            )
            break
        except Exception as exc:
            attempts += 1
            logger.warning(
                "RabbitMQ connection failed (attempt %d/10): %s", attempts, exc
            )
            await asyncio.sleep(1)
    else:
        raise RuntimeError("RabbitMQ unavailable after 10 attempts")

    app.state.mq_channel = await app.state.mq_connection.channel()
    await app.state.mq_channel.declare_queue(settings.task_queue, durable=True)
    logger.info("RabbitMQ connected")

    # Start auto-save background task
    shutdown_event = asyncio.Event()
    redis = await get_redis()
    auto_save_task = asyncio.create_task(
        auto_save_stale_sessions(redis, get_db, shutdown_event)
    )
    logger.info("Auto-save task started")

    yield

    # Shutdown: Clean up
    logger.info("App shutdown")
    shutdown_event.set()
    try:
        await asyncio.wait_for(auto_save_task, timeout=10.0)
    except asyncio.TimeoutError:
        logger.warning("Auto-save task did not complete in time, cancelling")
        auto_save_task.cancel()
    await app.state.mq_connection.close()
    await redis.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include game routes
app.include_router(game.router)


class ItemPayload(BaseModel):
    name: str
    payload: dict | None = None


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check all service dependencies."""
    checks = {}

    from sqlalchemy import text

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    return checks


@app.get("/translate")
async def api_translate(text: str, to_language: languages = "en"):
    """Translate text from English to the target language using Redis cache."""

    try:
        redis_client = await get_redis()
        result = await translate(text, to_language, redis_client)
        await redis_client.close()
        return {"text": text, "to_language": to_language, "translated": result}
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/items")
async def create_item(item: ItemPayload):
    """Enqueue an item on the RabbitMQ queue."""

    message = aio_pika.Message(body=item.model_dump_json().encode("utf-8"))
    await app.state.mq_channel.default_exchange.publish(
        message, routing_key=settings.task_queue
    )

    return {"status": "queued", "item": item}
