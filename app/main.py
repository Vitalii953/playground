from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import aio_pika
from app.config import settings
from app.database import get_db
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to RabbitMQ only if a queue name is configured.
    app.state.mq_connection = await aio_pika.connect_robust(str(settings.rabbitmq_url))
    app.state.mq_channel = await app.state.mq_connection.channel()
    # make sure the queue name matches whatever workers expect
    await app.state.mq_channel.declare_queue(settings.task_queue, durable=True)

    yield

    # Shutdown: Clean up
    await app.state.mq_connection.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text

    await db.execute(text("SELECT 1"))
    return {"status": "online", "database": "connected"}


class ItemPayload(BaseModel):
    """Schema for items published to the broker."""

    name: str
    value: int

# TODO: move to where this belongs

@app.post("/items")
async def create_item(item: ItemPayload):
    """enqueue a simple item on the RabbitMQ queue.

    The payload is JSON-encoded and sent to the ``task_queue`` so that
    the separate worker process can consume it.
    """

    # publish using the default exchange and routing key equal to queue name
    # pydantic 2 uses `model_dump_json` instead of `json` (see migration
    # warnings); the payload is a plain string that we send to the broker.
    message = aio_pika.Message(body=item.model_dump_json().encode("utf-8"))
    await app.state.mq_channel.default_exchange.publish(
        message, routing_key=settings.task_queue
    )

    # echo back for quick verification
    return {"status": "queued", "item": item}


