import asyncio
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from attr import frozen
from marshmallow import fields

from events.abc import Event, EventSchema, PublicKey
from events.consumer import EventConsumer
from events.registry import EventRegistry
from events.transports.queue import AsyncInMemoryTransport


@frozen(auto_attribs=True, kw_only=True, slots=True)
class TokenExpired(Event):
    """Access token has been expired."""

    token: str

    class Meta:
        """Event metadata."""

        event_type = "token_expired"
        version = "1.0"


@frozen(auto_attribs=True, kw_only=True, slots=True)
class TokenExpiredV2(Event):
    """Access token has been expired."""

    token: str

    class Meta:
        """Event metadata."""

        event_type = "token_expired"
        version = "2.0"


@frozen(auto_attribs=True, kw_only=True, slots=True)
class PasswordChanged(Event):
    """User password has been expired."""

    user_id: PublicKey

    class Meta:
        """Event metadata."""

        event_type = "password_changed"
        version = "1.0"


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


async def test_success(registry: EventRegistry, transport: AsyncInMemoryTransport, scheduler) -> None:
    """Successfully consume events from queue and call handlers."""
    event = TokenExpired(public_key=cast(PublicKey, uuid4()), token="top_secret")
    event_handler = AsyncMock()
    consumer = EventConsumer(registry=registry, transport=transport)
    consumer.register(handler=event_handler, event_cls=TokenExpired)
    await scheduler.spawn(consumer.consume())

    await transport.send(registry.dump(event))  # act

    await asyncio.sleep(1)
    event_handler.assert_called_once_with(event=event)


async def test_unsupported_version(registry: EventRegistry, transport: AsyncInMemoryTransport, scheduler) -> None:
    """Fail to consume events.

    Unsupported event version.
    """
    event = TokenExpiredV2(public_key=cast(PublicKey, uuid4()), token="top_secret")
    event_handler = AsyncMock()
    consumer = EventConsumer(registry=registry, transport=transport)
    consumer.register(handler=event_handler, event_cls=TokenExpired)
    await scheduler.spawn(consumer.consume())

    await transport.send(registry.dump(event))  # act

    await asyncio.sleep(1)
    event_handler.assert_not_called()


async def test_unknown_event(registry: EventRegistry, transport: AsyncInMemoryTransport, scheduler) -> None:
    """Fail to consume events.

    Unknown event.
    """
    event_handler = AsyncMock()
    consumer = EventConsumer(registry=registry, transport=transport)
    consumer.register(handler=event_handler, event_cls=TokenExpired)
    await scheduler.spawn(consumer.consume())

    await transport.send(
        {
            "__type__": "password_changed",
            "__version__": "2.0",
            "key": str(uuid4()),
        }
    )  # act

    await asyncio.sleep(1)
    event_handler.assert_not_called()
