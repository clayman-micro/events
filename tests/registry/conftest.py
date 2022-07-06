from typing import Callable, Optional, cast
from uuid import uuid4

import pytest
from attr import frozen
from marshmallow import fields, validate

from events.abc import Event, EventSchema, PublicKey
from events.registry import EventRegistry


@frozen(auto_attribs=True, kw_only=True, slots=True)
class AccountCreated(Event):
    """New account has been created."""

    name: str

    class Meta:
        """Event metadata."""

        event_type = "account_created"
        version = "1.0"


class AccountCreatedSchema(EventSchema):
    """Schema for AccountCreated serialization/deserialization."""

    event_cls = AccountCreated

    name = fields.Str(required=True, validate=validate.Length(min=2))


@pytest.fixture()
def create_event() -> Callable[[str], AccountCreated]:
    """Create AccountCreated event."""

    def builder(name: str, public_key: Optional[PublicKey] = None) -> AccountCreated:
        return AccountCreated(
            public_key=public_key or cast(PublicKey, uuid4()),
            name=name,
        )

    return builder


@pytest.fixture(scope="module")
def registry() -> EventRegistry:
    """Event manager instance for tests."""
    registry = EventRegistry()

    registry.register(event=AccountCreated, schema_cls=AccountCreatedSchema)

    return registry
