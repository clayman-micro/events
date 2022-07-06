from typing import Callable, Optional

from events.abc import PublicKey
from events.registry import EventRegistry
from tests.registry.conftest import AccountCreated


def test_success(registry: EventRegistry, create_event: Callable[[str, Optional[PublicKey]], AccountCreated]) -> None:
    """Serialize event with schema."""
    event = create_event("Foo", None)

    result = registry.dump(event)

    assert result == {
        "__type__": "account_created",
        "__version__": "1.0",
        "key": str(event.public_key),
        "name": "Foo",
    }
