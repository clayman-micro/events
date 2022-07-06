from typing import Any, AsyncGenerator

import aio_pika
import ujson
from aio_pika.channel import AbstractChannel
from aio_pika.exchange import AbstractExchange
from aio_pika.queue import AbstractQueue
from aio_pika.robust_connection import AbstractRobustConnection
from attr import define, field


@define(auto_attribs=True, kw_only=True, slots=True)
class AsyncRabbitMQTransport:
    """Event transport over RabbitMQ queues."""

    dsn: str
    exchange_name: str
    exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.DIRECT
    queue_name: str = "events"
    routing_key: str = "events"
    durable: bool = False

    connection: AbstractRobustConnection = field(init=False)
    channel: AbstractChannel = field(init=False)
    exchange: AbstractExchange = field(init=False)
    queue: AbstractQueue = field(init=False)

    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        self.connection = await aio_pika.connect_robust(url=self.dsn)
        self.channel = await self.connection.channel()

        await self.channel.set_qos(prefetch_count=10)

        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            type=self.exchange_type,
            durable=self.durable,
        )

        # Declaring queue
        self.queue = await self.channel.declare_queue(self.queue_name, auto_delete=True)

        # Binding queue
        await self.queue.bind(self.exchange)

    async def close(self) -> None:
        """Close connection to RabbitMQ."""
        await self.queue.unbind(self.exchange)
        await self.queue.delete()

        await self.connection.close()

    async def send(self, raw: dict[str, Any]) -> None:
        """Send event to RabbitMQ exchange."""
        message = aio_pika.Message(
            body=ujson.dumps(raw).encode(),
            content_type="application/json",
        )

        await self.exchange.publish(message, routing_key=self.routing_key)

    async def events(self) -> AsyncGenerator[dict[str, Any], None]:
        """Receive events from stream."""
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    if message.content_type != "application/json":
                        continue

                    body = ujson.loads(message.body)

                    yield body
