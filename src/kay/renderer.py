"""Rendering facilities."""

from __future__ import annotations

import asyncio
import curses
from abc import abstractmethod
from contextlib import contextmanager
from curses import ascii
from typing import ContextManager, Iterator, Optional, Protocol, Text, runtime_checkable

from kay import ansi, color
from kay.attr import Attr
from kay.color import Background, Color, Foreground
from kay.message import KeyMessage, Message


@runtime_checkable
class Renderer(ContextManager, Protocol):
    """Renderer protocol."""

    def __enter__(self) -> Renderer:
        """Enter context."""
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def into_raw_mode(self) -> Iterator[Renderer]:
        """Enter raw mode."""
        raise NotImplementedError

    @abstractmethod
    async def render(self, view: Text) -> None:
        """Render model."""
        raise NotImplementedError

    @abstractmethod
    async def next_message(self) -> Optional[Message]:
        """Get next message."""
        raise NotImplementedError


class CursesRenderer(Renderer):
    """Curses renderer."""

    _stdscr: curses._CursesWindow
    foreground: Optional[Color] = None
    background: Optional[Color] = None
    colors: dict[Optional[Color], int] = {
        None: -1,
        color.BLACK: 0,
        color.RED: 1,
        color.GREEN: 2,
        color.YELLOW: 3,
        color.BLUE: 4,
        color.MAGENTA: 5,
        color.CYAN: 6,
        color.WHITE: 7,
    }
    pairs: dict[tuple[Optional[Color], Optional[Color]], int] = {
        (None, None): -1,
        (color.WHITE, color.BLACK): 0,
    }

    def __init__(self) -> None:
        """Initialize."""
        self._stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()

    def __enter__(self) -> CursesRenderer:
        """Enter context."""
        self._stdscr.keypad(True)
        self._stdscr.nodelay(True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        self._stdscr.nodelay(False)
        self._stdscr.keypad(False)
        curses.endwin()

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

    def _reset_attributes(self) -> None:
        """Reset."""
        self.foreground = None
        self.background = None
        self._stdscr.attrset(curses.A_NORMAL)

    def _translate_attribute(self, attr: Attr) -> int:
        """
        Translate attribute.

        This **does not check for `Attribute.NORMAL`**, you have to do
        that yourself.
        """
        if attr == Attr.BOLD:
            return curses.A_BOLD
        if attr == Attr.FAINT:
            return curses.A_DIM
        if attr == Attr.UNDERLINE:
            return curses.A_UNDERLINE
        if attr == Attr.BLINK:
            return curses.A_BLINK
        if attr == Attr.REVERSE:
            return curses.A_REVERSE
        raise ValueError(f"unknown attribute: {attr}")

    def _translate_color(self, color: Foreground | Background) -> int:
        """
        Translate color.

        This returns the appropriate curses color pair based on the new color and the
        kept state.
        """
        if isinstance(color, Foreground):
            self.foreground = color.color
        if isinstance(color, Background):
            self.background = color.color
        if self.foreground not in self.colors:
            self.colors[self.foreground] = len(self.colors) - 1
            assert self.foreground is not None
            curses.init_color(self.colors[self.foreground], *self.foreground)
        if self.background not in self.colors:
            self.colors[self.background] = len(self.colors) - 1
            assert self.background is not None
            curses.init_color(self.colors[self.background], *self.background)
        if (self.foreground, self.background) not in self.pairs:
            self.pairs[(self.foreground, self.background)] = len(self.pairs) - 1
            curses.init_pair(
                self.pairs[(self.foreground, self.background)],
                self.colors[self.foreground],
                self.colors[self.background],
            )
        return curses.color_pair(self.pairs[(self.foreground, self.background)])

    # TODO: this does not seem to need to be a coroutine
    async def render(self, view: Text) -> None:
        """Render model."""
        await asyncio.sleep(1 / 120)
        self._stdscr.erase()
        self._reset_attributes()
        for piece in ansi.parse(view):
            if isinstance(piece, Text):
                self._stdscr.addstr(piece)
            else:
                if piece == Attr.NORMAL:
                    self._reset_attributes()
                elif isinstance(piece, Attr):
                    curses_attr = self._translate_attribute(piece)
                    self._stdscr.attron(curses_attr)
                else:
                    curses_attr = self._translate_color(piece)
                    self._stdscr.attron(curses_attr)
        self._stdscr.noutrefresh()
        curses.doupdate()

    async def next_message(self) -> Optional[Message]:
        """Get next message."""
        await asyncio.sleep(1 / 120)
        if (key := self._stdscr.getch()) == curses.ERR:
            return None

        if key == curses.KEY_UP:
            return KeyMessage("up")
        if key == curses.KEY_DOWN:
            return KeyMessage("down")
        if key == curses.KEY_LEFT:
            return KeyMessage("left")
        if key == curses.KEY_RIGHT:
            return KeyMessage("right")
        if key in {curses.KEY_ENTER, ascii.LF, ascii.CR}:
            # KEY_ENTER is rather unreliable, so we also accept ascii.LF
            # and ascii.CR.
            # See <https://stackoverflow.com/a/32255045/4039050>.
            return KeyMessage("enter")
        if key == ascii.SP:
            return KeyMessage("space")
        if ascii.isalnum(key) or ascii.isspace(key):
            return KeyMessage(chr(key))
        if ascii.isctrl(key):
            return KeyMessage(f"ctrl+{chr(ord('a') - 1 + key)}")
        return KeyMessage(f"unknown: {key}")
