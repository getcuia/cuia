"""Both terminal events and custom ones as message passing."""


from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Text


@dataclass(frozen=True)
class Message(ABC):
    """
    Simple message base class.

    This is a kind of a
    [marker interface](https://en.wikipedia.org/wiki/Marker_interface_pattern).
    Subclass this to create custom messages. There are no requirements for
    custom messages, but subclassing ensures that messages can be identified
    by the runtime and handled correctly.
    """


@dataclass(frozen=True)
class Quit(Message):
    """A message informing the application to quit."""




@dataclass(frozen=True)
class Event(Message):
    """A message informing the application of a terminal event."""

    value: Text


@dataclass(frozen=True)
class Key(Event):
    """A keyboard press event reported by the terminal."""

    @classmethod
    @property
    def BACKSPACE(cls) -> Key:
        """Return a key event for the backspace key."""
        return cls("backspace")

    @classmethod
    @property
    def LEFT(cls) -> Key:
        """Return a key event for the left arrow key."""
        return cls("left")

    @classmethod
    @property
    def RIGHT(cls) -> Key:
        """Return a key event for the right arrow key."""
        return cls("right")

    @classmethod
    @property
    def UP(cls) -> Key:
        """Return a key event for the up arrow key."""
        return cls("up")

    @classmethod
    @property
    def DOWN(cls) -> Key:
        """Return a key event for the down arrow key."""
        return cls("down")

    @classmethod
    @property
    def HOME(cls) -> Key:
        """Return a key event for the home key."""
        return cls("home")

    @classmethod
    @property
    def END(cls) -> Key:
        """Return a key event for the end key."""
        return cls("end")

    @classmethod
    @property
    def PAGE_UP(cls) -> Key:
        """Return a key event for the page up key."""
        return cls("pageup")

    @classmethod
    @property
    def PAGE_DOWN(cls) -> Key:
        """Return a key event for the page down key."""
        return cls("pagedown")

    @classmethod
    @property
    def BACK_TAB(cls) -> Key:
        """Return a key event for the backtab key."""
        return cls("backtab")

    @classmethod
    @property
    def DELETE(cls) -> Key:
        """Return a key event for the delete key."""
        return cls("delete")

    @classmethod
    @property
    def INSERT(cls) -> Key:
        """Return a key event for the insert key."""
        return cls("insert")

    @classmethod
    def F(cls, num: int) -> Key:
        """Return a key event for a function key."""
        return cls(f"f{num}")

    @classmethod
    def CHAR(cls, char: Text) -> Key:
        """Return a key event for a character key."""
        return cls(char)

    @classmethod
    def ALT(cls, char: Text) -> Key:
        """Return a key event for a combination of alt and character keys."""
        return cls(f"alt+{char}")

    @classmethod
    def CTRL(cls, char: Text) -> Key:
        """Return a key event for a combination of ctrl and character keys."""
        return cls(f"ctrl+{char}")

    @classmethod
    @property
    def NULL(cls) -> Key:
        """Return a key event for a null key."""
        return cls("null")

    @classmethod
    @property
    def ESCAPE(cls) -> Key:
        """Return a key event for the escape key."""
        return cls("escape")
