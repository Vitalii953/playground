from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import aio_pika
from app.core.config import settings
from app.core.database import get_db
from app.core.database import engine


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.info("App startup")
    
    try:
        # Startup: connect to RabbitMQ only if a queue name is configured.
        app.state.mq_connection = await aio_pika.connect_robust(str(settings.rabbitmq_url))
        app.state.mq_channel = await app.state.mq_connection.channel()
        # make sure the queue name matches whatever workers expect
        await app.state.mq_channel.declare_queue(settings.task_queue, durable=True)
        logger.info("RabbitMQ connected")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}", exc_info=True)
        raise

    yield

    # Shutdown: Clean up
    logger.info("App shutdown")
    await app.state.mq_connection.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check all service dependencies."""
    checks = {}
    
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"



@app.post("/items", response_model=dict)
async def create_item(item: ItemCreate):
    """Enqueue an item for processing."""
    try:
        logger.info(f"Enqueueing item: {item.name}")
        message = aio_pika.Message(body=item.model_dump_json().encode("utf-8"))
        await app.state.mq_channel.default_exchange.publish(
            message, routing_key=settings.task_queue
        )
        logger.info(f"Item {item.name} queued")
        return {"status": "queued", "item": item}
        
    except aio_pika.AMQPException as e:
        logger.error(f"RabbitMQ error: {e}")
        raise HTTPException(status_code=503, detail="Message broker unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    


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


