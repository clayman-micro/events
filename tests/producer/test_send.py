from typing import cast
from uuid import uuid4

import pytest
from attr import frozen
from marshmallow import fields

from events.abc import Event, EventSchema, PublicKey
from events.exceptions import UnsupportedEvent
from events.producer import EventProducer
from events.registry import EventRegistry
from events.transports.queue import AsyncInMemoryTransport


@frozen(auto_attribs=True, kw_only=True, slots=True)
class TokenExpired(Event):
    """Access token has been expired."""

    token: str

    class Meta:
        """Event metadata."""

        event_type = "token_expired"
        version = 1.0


@frozen(auto_attribs=True, kw_only=True, slots=True)
class PasswordChanged(Event):
    """User password has been expired."""

    user_id: PublicKey

    class Meta:
        """Event metadata."""

        event_type = "password_changed"
        version = 1.0


class TokenExpiredSchema(EventSchema):
    """Schema for TokenExpired event."""

    event_cls = TokenExpired

    token = fields.Str(required=True)


@pytest.fixture
def registry() -> EventRegistry:
    """Event registry for tests."""
    registry = EventRegistry()
    registry.register(TokenExpired, schema_cls=TokenExpiredSchema)

    return registry


async def test_success(registry: EventRegistry, transport: AsyncInMemoryTransport) -> None:
    """Successfully send event via producer."""
    event = TokenExpired(public_key=cast(PublicKey, uuid4()), token="top_secret")
    producer = EventProducer(registry=registry, transport=transport)

    await producer.send(event=event)

    message = transport.queue.get_nowait()
    assert message == {
        "__type__": "token_expired",
        "__version__": "1.0",
        "key": str(event.public_key),
        "token": "top_secret",
    }


async def test_fail(registry: EventRegistry, transport: AsyncInMemoryTransport) -> None:
    """Fail to send event via producer.

    Unsupported event.
    """
    event = PasswordChanged(public_key=cast(PublicKey, uuid4()), user_id=cast(PublicKey, uuid4()))
    producer = EventProducer(registry=registry, transport=transport)

    with pytest.raises(UnsupportedEvent):
        await producer.send(event=event)
