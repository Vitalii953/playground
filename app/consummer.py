from typing import Annotated
import aio_pika
import asyncio
import json
from app.config import settings
import redis.asyncio as redis


REDIS_CLIENT = Annotated[redis.Redis, "Async Redis client"]


async def process_message(message: aio_pika.abc.AbstractIncomingMessage, redis_client: REDIS_CLIENT) -> None:
    async with message.process():
        body = message.body.decode()

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            # if not JSON just store raw string
            data = body

        await redis_client.lpush("items", data)    # type: ignore

        # simulate some work
        await asyncio.sleep(1)


async def main():
    connection = await aio_pika.connect_robust(str(settings.rabbitmq_url))
    channel = await connection.channel()

    # declare the same queue that the API uses
    queue = await channel.declare_queue(settings.task_queue, durable=True)

    # setup redis client once
    redis_client = redis.from_url(str(settings.redis_url), encoding="utf-8", decode_responses=True)

    # consumer callback needs redis_client; use lambda to bind
    await queue.consume(lambda msg: process_message(msg, redis_client))

    try:
        await asyncio.Future()  # Run forever
    finally:
        await connection.close()
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
