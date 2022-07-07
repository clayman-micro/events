import abc
import uuid
from typing import Any, AsyncGenerator, NewType, Protocol, Type

from attr import asdict, frozen
from marshmallow import Schema, ValidationError, fields, post_load, pre_dump, validate, validates

PublicKey = NewType("PublicKey", uuid.UUID)


@frozen(auto_attribs=True, kw_only=True, slots=True)
class Event(metaclass=abc.ABCMeta):
    """Base class for events."""

    public_key: PublicKey

    class Meta:
        """Event meta info."""

        event_type: str = "event"
        version: str = "1.0"


class EventSchema(Schema):
    """Base schema for event serialization/deserialization."""

    event_cls: Type[Event]

    event_type = fields.Str(required=True, data_key="__type__")
    version = fields.Str(required=True, data_key="__version__", validate=validate.Regexp(r"(\d+).(\d+)"))

    public_key = fields.UUID(required=True, data_key="key")

    @validates("event_type")
    def validate_event_type(self, value):
        """Validate event type match."""
        if value != self.event_cls.Meta.event_type:
            raise ValidationError("Invalid event type")

    @validates("version")
    def validate_version(self, value):
        """Validate event type match."""
        if value != self.event_cls.Meta.version:
            raise ValidationError("Invalid event version")

    @pre_dump
    def serialize_event(self, event: Event, **kwargs):
        """Serialize event object."""
        serialized = asdict(event)

        serialized.update(
            {
                "event_type": event.Meta.event_type,
                "version": event.Meta.version,
            }
        )

        return serialized

    @post_load
    def create_event(self, data, **kwargs):
        """Deserialize event object."""
        return self.event_cls(**{key: value for key, value in data.items() if key not in ("event_type", "version")})


class EventTransport(Protocol):
    """Basic event transport protocol."""

    @abc.abstractmethod
    async def connect(self) -> None:
        """Connect to message broker."""
        ...

    @abc.abstractmethod
    async def close(self) -> None:
        """Close connection to message broker."""

    @abc.abstractmethod
    async def send(self, event: dict[str, Any]) -> None:
        """Send new event."""
        ...

    @abc.abstractmethod
    def events(self) -> AsyncGenerator[dict[str, Any], None]:
        """Receive events from stream."""
        ...
