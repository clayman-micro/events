from attr import define

from events.abc import Event, EventTransport
from events.registry import EventRegistry


@define(auto_attribs=True, kw_only=True, slots=True)
class EventProducer:
    """Event emitter to send events to bus."""

    registry: EventRegistry
    transport: EventTransport

    async def send(self, event: Event) -> None:
        """Send new event to event bus."""
        await self.transport.send(self.registry.dump(event))
