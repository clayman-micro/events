from asyncio.queues import Queue
from typing import Any, AsyncGenerator

from attr import define, field


@define(auto_attribs=True, kw_only=True, slots=True)
class AsyncInMemoryTransport:
    """Event transport over in-memory queue."""

    queue: Queue = field(init=False)

    async def connect(self) -> None:
        """Connect to queue."""
        self.queue = Queue()

    async def close(self) -> None:
        """Disconnect from queue."""

    async def send(self, event: dict[str, Any]) -> None:
        """Send new event."""
        await self.queue.put(event)

    async def events(self) -> AsyncGenerator[dict[str, Any], None]:
        """Receive events from stream."""
        while True:
            raw = await self.queue.get()
            yield raw
