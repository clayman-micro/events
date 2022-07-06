from typing import Callable, cast
from uuid import uuid4

import pytest
from marshmallow import ValidationError

from events.abc import PublicKey
from events.registry import EventRegistry
from tests.registry.conftest import AccountCreated


def test_success(registry: EventRegistry, create_event: Callable[[str, PublicKey], AccountCreated]) -> None:
    """Deserialize event with schema."""
    public_key = cast(PublicKey, uuid4())
    expected = create_event("Foo", public_key)

    result = registry.load_from_dict(
        {
            "__type__": "account_created",
            "__version__": "1.0",
            "key": str(public_key),
            "name": "Foo",
        }
    )

    assert result == expected


def test_failed(registry: EventRegistry, create_event: Callable[[str, PublicKey], AccountCreated]) -> None:
    """Validation failed, unsupported version."""
    public_key = cast(PublicKey, uuid4())

    with pytest.raises(ValidationError):
        registry.load_from_dict(
            {
                "__type__": "account_created",
                "__version__": "2.0",
                "key": str(public_key),
                "name": "Foo",
            }
        )
