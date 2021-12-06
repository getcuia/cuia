"""A renderer that uses Python's standard curses library."""

from __future__ import annotations

import curses
from contextlib import contextmanager
from curses import ascii
from dataclasses import dataclass, field
from types import TracebackType
from typing import Iterator, Optional, Text, Type

from cusser import Cusser

from ..message import Key, Message, Unsupported
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
        try:
            key = self.stdscr.get_wch()
        except curses.error:
            return None

        if isinstance(key, int):
            ikey = key
            key = chr(key)
        else:
            ikey = ord(key)

        if ikey in {ascii.BS, curses.KEY_BACKSPACE}:
            # Backspace (unreliable, so we also accept the ASCII BS charater).
            return Key.BACKSPACE
        elif ikey in {ascii.CR, ascii.LF, curses.KEY_ENTER}:
            # Enter or send (unreliable, so we also accept carriage returns and
            # line feeds. See <https://stackoverflow.com/a/32255045/4039050>.
            return Key.ENTER
        elif ikey == curses.KEY_LEFT:
            # Left-arrow
            return Key.LEFT
        elif ikey == curses.KEY_RIGHT:
            # Right-arrow
            return Key.RIGHT
        elif ikey == curses.KEY_UP:
            # Up-arrow
            return Key.UP
        elif ikey == curses.KEY_DOWN:
            # Down-arrow
            return Key.DOWN
        elif ikey == curses.KEY_SLEFT:
            # Shift+left-arrow
            return Key.SHIFT(Key.LEFT)
        elif ikey == curses.KEY_SRIGHT:
            # Shift+right-arrow
            return Key.SHIFT(Key.RIGHT)
        elif ikey == curses.KEY_SR:
            # Shift+up-arrow (scroll one backward)
            return Key.SHIFT(Key.UP)
        elif ikey == curses.KEY_SF:
            # Shift+down-arrow (scroll one forward)
            return Key.SHIFT(Key.DOWN)
        elif ikey == curses.KEY_HOME:
            # Home key (upward+left arrow)
            return Key.HOME
        elif ikey == curses.KEY_END:
            # End
            return Key.END
        elif ikey == curses.KEY_PPAGE:
            # Previous page
            return Key.PAGE_UP
        elif ikey == curses.KEY_NPAGE:
            # Next page
            return Key.PAGE_DOWN
        elif ikey == curses.KEY_SHOME:
            # Shift+home key
            return Key.SHIFT(Key.HOME)
        elif ikey == curses.KEY_SEND:
            # Shift+end key
            return Key.SHIFT(Key.END)
        elif ikey == curses.KEY_SPREVIOUS:
            # Shift+previous page
            return Key.SHIFT(Key.PAGE_UP)
        elif ikey == curses.KEY_SNEXT:
            # Shift+next page
            return Key.SHIFT(Key.PAGE_DOWN)
        elif ikey == ascii.TAB:
            # Tab key
            return Key.TAB
        elif ikey == curses.KEY_BTAB:
            # Shift+tab key (back tab)
            return Key.SHIFT(Key.TAB)
        elif ikey in {ascii.DEL, curses.KEY_DC}:
            # Delete character
            return Key.DELETE
        elif ikey == curses.KEY_SDC:
            # Shift+delete character
            return Key.SHIFT(Key.DELETE)
        elif ikey == curses.KEY_IC:
            # Insert char or enter insert mode
            return Key.INSERT
        elif curses.KEY_F0 <= ikey <= curses.KEY_F12:
            # Function keys.
            return Key.F(ikey - curses.KEY_F0)
        elif curses.KEY_F13 <= ikey <= curses.KEY_F24:
            # Shift+function keys.
            return Key.SHIFT(Key.F(ikey - curses.KEY_F12))
        elif curses.KEY_F25 <= ikey <= curses.KEY_F36:
            # Control+function keys.
            return Key.CTRL(Key.F(ikey - curses.KEY_F24))
        elif curses.KEY_F37 <= ikey <= curses.KEY_F48:
            # Control+shift+function keys.
            return Key.CTRL(Key.SHIFT(Key.F(ikey - curses.KEY_F36)))
        elif curses.KEY_F49 <= ikey <= curses.KEY_F60:
            # Alt+function keys.
            return Key.ALT(Key.F(ikey - curses.KEY_F48))
        elif key == ascii.NUL:
            # Null key
            return Key.NULL
        elif ikey == ascii.ESC:
            # This assumes no delay is set to True.
            if (next_key := self.next_message()) is None:
                # Escape key
                return Key.ESCAPE
            # Alt+key
            assert isinstance(next_key, Key)
            return Key.ALT(next_key)
        elif ascii.isctrl(ikey):
            # Control+key
            return Key.CTRL(chr(ord("a") + ikey - 1))
        elif ascii.ismeta(ikey):
            # Meta+key
            return Key.META(key)
        elif ascii.isprint(ikey):
            # Any other alphanumeric key
            return Key.CHAR(key)

        # https://stackoverflow.com/a/32794353/4039050

        return Unsupported(curses.keyname(ikey))

    def __enter__(self) -> CursesRenderer:
        """Enter context."""
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        curses.meta(True)
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context."""
        curses.meta(False)
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
