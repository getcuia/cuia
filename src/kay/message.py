"""Terminal events."""


from typing import Protocol


class Message(Protocol):
    """Event protocol."""

    pass


class QuitMessage(Message):
    """Quit event."""

    pass


class KeyMessage(Message):
    """Key event."""

    def __init__(self, key):
        """Initialize a key event."""
        self.key = key
