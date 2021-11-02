"""Terminal events."""


from typing import Protocol


class Event(Protocol):
    """Event protocol."""

    pass


class QuitEvent(Event):
    """Quit event."""

    pass


class KeyEvent(Event):
    """Key event."""

    def __init__(self, key):
        """Initialize a key event."""
        self.key = key
