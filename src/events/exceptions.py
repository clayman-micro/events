import attrs


@attrs.define(kw_only=True, slots=True)
class BaseEventException(Exception):
    """Базовая ошибка, связанная с событиями."""

    message: str


@attrs.define(kw_only=True, slots=True)
class InvalidEvent(BaseEventException):
    """Неправильный формат события."""


@attrs.define(kw_only=True, slots=True)
class EventNotFound(BaseEventException):
    """Событие не найдено."""


@attrs.define(kw_only=True, slots=True)
class EventAlreadyExist(BaseEventException):
    """Событие такого типа уже существует."""
