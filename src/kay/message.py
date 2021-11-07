"""Terminal events."""


from __future__ import annotations

from typing import Protocol, Text, runtime_checkable


@runtime_checkable
class Message(Protocol):
    """Event protocol."""


class QuitMessage(Message):
    """Quit event."""


class KeyMessage(Message):
    """Keyboard event."""

    key: Text

    def __init__(self, key: Text):
        """Initialize a keyboard event."""
        super().__init__()
        self.key = key

    def __repr__(self) -> Text:
        """Return a string representation of the keyboard event."""
        return f"KeyMessage({repr(self.key)})"

    def __str__(self) -> Text:
        """Return a friendly representation of the keyboard event."""
        return self.key
