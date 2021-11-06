"""Rendering facilities."""

from __future__ import annotations

import asyncio
import curses
from abc import abstractmethod
from contextlib import contextmanager
from curses import ascii
from typing import ContextManager, Iterator, Optional, Protocol, Text

from kay import ansi
from kay.attr import Attr
from kay.message import KeyMessage, Message


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

    @staticmethod
    def _translate_attribute(attr: Attr) -> int:
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

    async def render(self, view: Text) -> None:
        """Render model."""
        await asyncio.sleep(1 / 120)
        self._stdscr.erase()
        for piece in ansi.parse(view):
            if isinstance(piece, Text):
                self._stdscr.addstr(piece)
            else:
                if piece == Attr.NORMAL:
                    self._stdscr.attrset(curses.A_NORMAL)
                else:
                    curses_attr = CursesRenderer._translate_attribute(piece)
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
