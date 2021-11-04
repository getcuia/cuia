"""Terminal events."""


from __future__ import annotations

import curses
from curses import ascii
from typing import Optional, Protocol, Text


class Message(Protocol):
    """Event protocol."""

    @staticmethod
    def from_curses(win: curses._CursesWindow) -> Optional[Message]:
        """Return a message of known type from curses window."""
        if (ch := win.getch()) == curses.ERR:
            return None

        return KeyMessage(ch)


class QuitMessage(Message):
    """Quit event."""

    pass


class KeyMessage(Message):
    """Keyboard event."""

    def __init__(self, ch: int):
        """Initialize a keyboard event."""
        self.key = ch

    def __repr__(self) -> Text:
        """Return a string representation of the keyboard event."""
        return f"KeyMessage({repr(self.key)})"

    def __str__(self) -> Text:
        """Return a friendly representation of the keyboard event."""
        if self.key == curses.KEY_UP:
            return "up"
        elif self.key == curses.KEY_DOWN:
            return "down"
        elif self.key == curses.KEY_LEFT:
            return "left"
        elif self.key == curses.KEY_RIGHT:
            return "right"
        elif self.key in {curses.KEY_ENTER, ascii.LF, ascii.CR}:
            # KEY_ENTER is rather unreliable, so we also accept ascii.LF
            # and ascii.CR.
            # See <https://stackoverflow.com/a/32255045/4039050>.
            return "enter"
        elif self.key == ascii.SP:
            return "space"
        # TODO: check ctrl
        elif ascii.isalnum(self.key) or ascii.isspace(self.key):
            return chr(self.key)
        else:
            return f"unknown key {self.key}"
