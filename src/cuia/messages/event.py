"""Terminal events."""


from __future__ import annotations

from curses import ascii
from dataclasses import dataclass
from enum import Flag, auto
from typing import Generic, Text, TypeVar

from .message import Message

T = TypeVar("T")


@dataclass(frozen=True)
class Event(Message, Generic[T]):
    """A message informing the application of a terminal event."""

    value: T


class KeyModifier(Flag):
    """
    Enumeration of key modifiers.

    This is used to specify which modifier keys are pressed when a key is
    pressed.
    """

    NONE = 0
    ALT = auto()
    CTRL = auto()
    META = auto()
    SHIFT = auto()


@dataclass(frozen=True)
class Key(Event[Text]):
    """A keyboard press event reported by the terminal."""

    modifier: KeyModifier = KeyModifier.NONE

    def __post_init__(self):
        """
        Initialize the key.

        This method is called after the key is constructed. It is used to
        validate the key.
        """
        if not isinstance(self.value, Text):
            if isinstance(self.value, int):
                object.__setattr__(self, "value", chr(self.value))
            else:
                raise TypeError(f"{self.value} is not a valid key value.")

        assert self.value, "Key value cannot be empty."

    @classmethod
    def CHAR(cls, char: Text | int) -> Key:
        """Return a key event for a normal character key."""
        return cls(char)  # type: ignore

    @classmethod
    def ALT(cls, key: Key | Text | int) -> Key:
        """
        Return a key event for an alt modified character.

        Note that certain keys may not be modifiable with `alt`, due to limitations of
        terminals.
        """
        if isinstance(key, Key):
            return cls(value=key.value, modifier=key.modifier | KeyModifier.ALT)
        return cls(value=key, modifier=KeyModifier.ALT)  # type: ignore

    @classmethod
    def CTRL(cls, key: Key | Text | int) -> Key:
        """
        Return a key event for a ctrl modified character.

        Note that certain keys may not be modifiable with `ctrl`, due to limitations of
        terminals.
        """
        if isinstance(key, Key):
            return cls(value=key.value, modifier=key.modifier | KeyModifier.CTRL)
        return cls(value=key, modifier=KeyModifier.CTRL)  # type: ignore

    @classmethod
    def META(cls, key: Key | Text | int) -> Key:
        """
        Return a key event for a meta modified character.

        Note that certain keys may not be modifiable with `meta`, due to limitations of
        terminals.
        """
        if isinstance(key, Key):
            return cls(value=key.value, modifier=key.modifier | KeyModifier.META)
        return cls(value=key, modifier=KeyModifier.META)  # type: ignore

    @classmethod
    def SHIFT(cls, key: Key | Text | int) -> Key:
        """
        Return a key event for a shift modified character.

        Note that certain keys may not be modifiable with `shift`, due to limitations of
        terminals.
        """
        if isinstance(key, Key):
            return cls(value=key.value, modifier=key.modifier | KeyModifier.SHIFT)
        return cls(value=key, modifier=KeyModifier.SHIFT)  # type: ignore

    @classmethod
    def F(cls, num: int) -> Key:
        """
        Return a key event for a function key.

        We make no guarantee that function keys above F12 are supported.
        """
        return cls(f"f{num}")

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
    def INSERT(cls) -> Key:
        """Return a key event for the insert key."""
        return cls("insert")

    @classmethod
    @property
    def BACKSPACE(cls) -> Key:
        """Return a key event for the backspace key."""
        return cls(ascii.BS)  # type: ignore

    @classmethod
    @property
    def ENTER(cls) -> Key:
        """Return a key event for the enter key."""
        return cls(ascii.NL)  # type: ignore

    @classmethod
    @property
    def TAB(cls) -> Key:
        """Return a key event for the tab key."""
        return cls(ascii.TAB)  # type: ignore

    @classmethod
    @property
    def DELETE(cls) -> Key:
        """Return a key event for the delete key."""
        return cls(ascii.DEL)  # type: ignore

    @classmethod
    @property
    def SPACE(cls) -> Key:
        """Return a key event for the space key."""
        return cls(ascii.SP)  # type: ignore

    @classmethod
    @property
    def NULL(cls) -> Key:
        """Return a key event for a null byte."""
        return cls(ascii.NUL)  # type: ignore

    @classmethod
    @property
    def ESCAPE(cls) -> Key:
        """Return a key event for the escape key."""
        return cls(ascii.ESC)  # type: ignore


@dataclass(frozen=True)
class Resize(Event[tuple[int, int]]):
    """A terminal resize event."""


@dataclass(frozen=True)
class Unsupported(Event[bytes]):
    """A message informing the application of a currently unsupported terminal event."""
