class UnsupportedEvent(Exception):
    """Application does not support event with given type."""

    def __init__(self, event_type: str) -> None:
        self._event_type = event_type

    @property
    def event_type(self) -> str:
        """Type of event."""
        return self._event_type
