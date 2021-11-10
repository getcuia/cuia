"""Terminal events as message passing."""


from __future__ import annotations

from typing import Protocol, Text, runtime_checkable


@runtime_checkable
class Message(Protocol):
    """Simple message protocol."""


class QuitMessage(Message):
    """A message informing the application to quit."""


class KeyMessage(Message):
    """A message generated by a keyboard event."""

    key: Text
    """The key pressed."""

    def __init__(self, key: Text):
        """Initialize a keyboard message."""
        super().__init__()
        self.key = key

    def __repr__(self) -> Text:
        """Return a string representation of the keyboard message."""
        return f"KeyMessage({repr(self.key)})"

    def __str__(self) -> Text:
        """Return a friendly representation of the keyboard message."""
        return self.key
