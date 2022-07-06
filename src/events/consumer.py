from collections import defaultdict
from typing import Awaitable, Callable, Type

from attr import define, field
from mypy_extensions import NamedArg

from events.abc import Event, EventTransport
from events.exceptions import UnsupportedEvent
from events.registry import EventRegistry

EventHandler = Callable[[NamedArg(type=Event, name="event")], Awaitable[None]]  # noqa: F821


@define(auto_attribs=True, kw_only=True, slots=True)
class EventConsumer:
    """Event bus."""

    registry: EventRegistry
    transport: EventTransport

    handlers: dict[str, set[EventHandler]] = field(init=False, factory=lambda: defaultdict(set))

    def register(self, handler: EventHandler, event_cls: Type[Event]) -> None:
        """Registry new handler for event."""
        self.handlers[event_cls.Meta.event_type].add(handler)

    async def consume(self) -> None:
        """Consume events from transport and call apropriate handlers."""
        if not self.handlers:
            raise ValueError("Event consumer doesn't have handlers for events")

        async for raw_event in self.transport.events():
            try:
                event = self.registry.load_from_dict(raw_event)
            except UnsupportedEvent:
                continue

            for handler in self.handlers.get(event.Meta.event_type, []):
                await handler(event=event)
