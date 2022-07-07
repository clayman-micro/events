from typing import Any, Type

from attr import define, field

from events.abc import Event, EventSchema
from events.exceptions import UnsupportedEvent


@define(auto_attribs=True, kw_only=True, slots=True)
class EventRegistry:
    """Registry of supported events."""

    schemas: dict[str, EventSchema] = field(init=False, factory=dict)

    def register(self, event: Type[Event], schema_cls: Type[EventSchema]) -> None:
        """Register new event type."""
        self.schemas[event.Meta.event_type] = schema_cls()

    def dump(self, event: Event) -> dict[str, Any]:
        """Serialize event."""
        event_type = event.Meta.event_type

        schema = self.schemas.get(event_type, None)
        if schema:
            return schema.dump(event)

        raise UnsupportedEvent(event_type=event_type)

    def load_from_dict(self, raw: dict[str, Any]) -> Event:
        """Deserialize event."""
        event_type = raw.get("__type__", None)
        if event_type:
            schema = self.schemas.get(event_type)
            if schema:
                return schema.load(raw)

            raise ValueError("Unsupported event")

        raise ValueError("Unknown event")
