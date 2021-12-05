"""A renderer that uses Python's standard curses library."""

from __future__ import annotations

import curses
from contextlib import contextmanager
from curses import ascii
from dataclasses import dataclass, field
from types import TracebackType
from typing import Iterator, Optional, Text, Type

from cusser import Cusser

from ..message import Key, Message
from .renderer import Renderer


@dataclass
class CursesRenderer(Renderer):
    """
    Curses renderer.

    Examples
    --------
    >>> with CursesRenderer() as renderer:
    ...     renderer.render("Hello, world!")  # doctest: +SKIP
    """

    stdscr: Cusser = field(default_factory=lambda: Cusser(curses.initscr()))

    def render(self, screen: Text) -> None:
        """Render a screen."""
        self.stdscr.erase()
        self.stdscr.addstr("\033[m")
        self.stdscr.addstr(screen)
        self.stdscr.noutrefresh()
        curses.doupdate()

    def next_message(self) -> Optional[Message]:
        """Get next message."""
        if (key := self.stdscr.getch()) == curses.ERR:
            return None

        if key in {ascii.BS, curses.KEY_BACKSPACE}:
            # Backspace (unreliable)
            return Key.BACKSPACE
        elif key in {ascii.CR, ascii.LF, curses.KEY_ENTER}:
            # Enter or send (unreliable, so we also accept carriage returns and line feeds .
            # See <https://stackoverflow.com/a/32255045/4039050>.
            return Key.ENTER
        elif key == curses.KEY_LEFT:
            # Left-arrow
            return Key.LEFT
        elif key == curses.KEY_RIGHT:
            # Right-arrow
            return Key.RIGHT
        elif key == curses.KEY_UP:
            # Up-arrow
            return Key.UP
        elif key == curses.KEY_DOWN:
            # Down-arrow
            return Key.DOWN
        elif key == curses.KEY_HOME:
            # Home key (upward+left arrow)
            return Key.HOME
        elif key == curses.KEY_END:
            # End
            return Key.END
        elif key == curses.KEY_PPAGE:
            # Previous page
            return Key.PAGE_UP
        elif key == curses.KEY_NPAGE:
            # Next page
            return Key.PAGE_DOWN
        elif key == ascii.TAB:
            # Tab key
            return Key.TAB
        elif key == curses.KEY_BTAB:
            # Back tab
            return Key.BACK_TAB
        elif key in {ascii.DEL, curses.KEY_DC}:
            # Delete character
            return Key.DELETE
        elif key == curses.KEY_IC:
            # Insert char or enter insert mode
            return Key.INSERT
        elif curses.KEY_F0 <= key <= curses.KEY_F63:
            # Function keys. Up to 64 function keys are supported.
            return Key.F(key - curses.KEY_F0)
        elif key == ascii.ESC:
            # This assumes no delay is set to True.
            if (next_key := self.stdscr.getch()) == curses.ERR:
                # Escape key
                return Key.ESCAPE
            # Alt plus key
            return Key.ALT(chr(next_key))
        elif ascii.isctrl(key):
            # Control plus key
            return Key.CTRL(chr(ord("a") - 1 + key))
        elif key == ascii.NUL:
            # Null key
            return Key.NULL
        elif ascii.isprint(key):
            # Any other alphanumeric key
            return Key.CHAR(chr(key))

        raise ValueError(f"unknown key: {key!r} ({chr(key)})")

    def __enter__(self) -> CursesRenderer:
        """Enter context."""
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context."""
        self.stdscr.nodelay(False)
        self.stdscr.keypad(False)
        curses.endwin()
        return None

    @contextmanager
    def into_raw_mode(self) -> Iterator[CursesRenderer]:
        """Enter raw mode."""
        curses.noecho()
        curses.raw()
        try:
            yield self
        finally:
            curses.noraw()
            curses.echo()

    @contextmanager
    def hide_cursor(self) -> Iterator[CursesRenderer]:
        """Hide the cursor."""
        curses.curs_set(0)
        try:
            yield self
        finally:
            curses.curs_set(1)
