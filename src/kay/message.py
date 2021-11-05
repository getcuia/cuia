"""Terminal events."""


from __future__ import annotations

from typing import Protocol, Text


class Message(Protocol):
    """Event protocol."""

    pass


class QuitMessage(Message):
    """Quit event."""

    pass


class KeyMessage(Message):
    """Keyboard event."""

    key: Text

    def __init__(self, key: Text):
        """Initialize a keyboard event."""
        self.key = key

    def __repr__(self) -> Text:
        """Return a string representation of the keyboard event."""
        return f"KeyMessage({repr(self.key)})"

    def __str__(self) -> Text:
        """Return a friendly representation of the keyboard event."""
        return self.key
