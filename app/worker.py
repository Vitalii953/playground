import asyncio
import aio_pika
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")


async def process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():
        body = message.body.decode()
        print(f" [x] Received message: {body}")
        # This is where you'd write to Redis or do 'work'
        await asyncio.sleep(1)


async def main():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    queue = await channel.declare_queue("task_queue", durable=True)
    await queue.consume(process_message)

    print(" [*] Worker waiting for messages. To exit press CTRL+C")
    await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
