"""A renderer that uses Python's standard curses library."""

from __future__ import annotations

import curses
from contextlib import contextmanager
from curses import ascii
from dataclasses import dataclass, field
from types import TracebackType
from typing import Iterator, Optional, Text, Type

from cusser import Cusser

from ..messages import Key, Message, Unsupported
from .renderer import Renderer

ORD_A = ord("a")


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

    def next_message(self) -> Optional[Message]:  # noqa: C901
        """Get next message."""
        try:
            key = self.stdscr.get_wch()
        except curses.error:
            return None

        if isinstance(key, int):
            ikey = key
            key = chr(key)
        elif isinstance(key, (bytes, Text)):
            ikey = ord(key)
        else:
            raise TypeError(f"unexpected type: {type(key)} ({key!r})")

        # Left-arrow key
        if ikey == curses.KEY_LEFT:
            return Key.LEFT  # type: ignore

        # Right-arrow key
        if ikey == curses.KEY_RIGHT:
            return Key.RIGHT  # type: ignore

        # Up-arrow key
        if ikey == curses.KEY_UP:
            return Key.UP  # type: ignore

        # Down-arrow key
        if ikey == curses.KEY_DOWN:
            return Key.DOWN  # type: ignore

        # Shift+left-arrow key
        if ikey == curses.KEY_SLEFT:
            return Key.SHIFT(Key.LEFT)  # type: ignore

        # Shift+right-arrow key
        if ikey == curses.KEY_SRIGHT:
            return Key.SHIFT(Key.RIGHT)  # type: ignore

        # Shift+up-arrow key (scroll one backward)
        if ikey == curses.KEY_SR:
            return Key.SHIFT(Key.UP)  # type: ignore

        # Shift+down-arrow key (scroll one forward)
        if ikey == curses.KEY_SF:
            return Key.SHIFT(Key.DOWN)  # type: ignore

        # Home key (upward+left arrow)
        if ikey == curses.KEY_HOME:
            return Key.HOME  # type: ignore

        # End key
        if ikey == curses.KEY_END:
            return Key.END  # type: ignore

        # Previous page key
        if ikey == curses.KEY_PPAGE:
            return Key.PAGE_UP  # type: ignore

        # Next page key
        if ikey == curses.KEY_NPAGE:
            return Key.PAGE_DOWN  # type: ignore

        # Shift+home key
        if ikey == curses.KEY_SHOME:
            return Key.SHIFT(Key.HOME)  # type: ignore

        # Shift+end key
        if ikey == curses.KEY_SEND:
            return Key.SHIFT(Key.END)  # type: ignore

        # Shift+previous page key
        if ikey == curses.KEY_SPREVIOUS:
            return Key.SHIFT(Key.PAGE_UP)  # type: ignore

        # Shift+next page key
        if ikey == curses.KEY_SNEXT:
            return Key.SHIFT(Key.PAGE_DOWN)  # type: ignore

        # Shift+tab key (back tab)
        if ikey == curses.KEY_BTAB:
            return Key.SHIFT(Key.TAB)  # type: ignore

        # Shift+delete character key
        if ikey == curses.KEY_SDC:
            return Key.SHIFT(Key.DELETE)  # type: ignore

        # Insert char or enter insert mode key
        if ikey == curses.KEY_IC:
            return Key.INSERT  # type: ignore

        # Function keys
        if curses.KEY_F0 <= ikey <= curses.KEY_F12:
            return Key.F(ikey - curses.KEY_F0)

        # Shift+function key
        if curses.KEY_F13 <= ikey <= curses.KEY_F24:
            return Key.SHIFT(Key.F(ikey - curses.KEY_F12))

        # Control+function key
        if curses.KEY_F25 <= ikey <= curses.KEY_F36:
            return Key.CTRL(Key.F(ikey - curses.KEY_F24))

        # Control+shift+function key
        if curses.KEY_F37 <= ikey <= curses.KEY_F48:
            return Key.CTRL(Key.SHIFT(Key.F(ikey - curses.KEY_F36)))

        # Alt+function key
        if curses.KEY_F49 <= ikey <= curses.KEY_F60:
            return Key.ALT(Key.F(ikey - curses.KEY_F48))

        # Backspace key (unreliable, so we also accept the ASCII BS charater).
        if ikey in {ascii.BS, curses.KEY_BACKSPACE}:
            return Key.BACKSPACE  # type: ignore

        # Enter or send key (unreliable, so we also accept carriage returns and
        # line feeds. See <https://stackoverflow.com/a/32255045/4039050>.
        if ikey in {ascii.CR, ascii.LF, curses.KEY_ENTER}:
            return Key.ENTER  # type: ignore

        # Tab key
        if ikey == ascii.TAB:
            return Key.TAB  # type: ignore

        # Delete character key
        if ikey in {ascii.DEL, curses.KEY_DC}:
            return Key.DELETE  # type: ignore

        # Null key
        if key == ascii.NUL:
            return Key.NULL  # type: ignore

        if ikey == ascii.ESC:
            # This assumes no delay is set to True
            if (next_key := self.next_message()) is None:
                # Escape key
                return Key.ESCAPE  # type: ignore

            # Alt+other key
            assert isinstance(next_key, Key)
            return Key.ALT(next_key)

        # Control+other key
        if ascii.isctrl(ikey):
            return Key.CTRL(chr(ORD_A + ikey - 1))

        # Meta+other key (might also be some special key)
        if ascii.ismeta(ikey):
            return Key.META(key)

        # Any other printable character key
        if ascii.isprint(ikey):
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
