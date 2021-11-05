"""Rendering facilities."""

from __future__ import annotations

import asyncio
import curses
from abc import abstractmethod
from contextlib import contextmanager
from curses import ascii
from typing import ContextManager, Iterator, Optional, Protocol, Text

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

    def __enter__(self) -> CursesRenderer:
        """Enter context."""
        self._stdscr.nodelay(True)
        self._stdscr.keypad(True)
        # More: https://github.com/gyscos/cursive/blob/c4c74c02996f3f6e66136b51a4d83d2562af740a/cursive/src/backends/curses/n.rs#L133-L143
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        self._stdscr.keypad(False)
        self._stdscr.nodelay(False)
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

    async def render(self, view: Text) -> None:
        """Render model."""
        self._stdscr.erase()
        self._stdscr.addstr(view)
        self._stdscr.noutrefresh()
        curses.doupdate()
        await asyncio.sleep(1 / 60)

    async def next_message(self) -> Optional[Message]:
        """Get next message."""
        if (key := self._stdscr.getch()) == curses.ERR:
            return None

        if key == curses.KEY_UP:
            return KeyMessage("up")
        elif key == curses.KEY_DOWN:
            return KeyMessage("down")
        elif key == curses.KEY_LEFT:
            return KeyMessage("left")
        elif key == curses.KEY_RIGHT:
            return KeyMessage("right")
        elif key in {curses.KEY_ENTER, ascii.LF, ascii.CR}:
            # KEY_ENTER is rather unreliable, so we also accept ascii.LF
            # and ascii.CR.
            # See <https://stackoverflow.com/a/32255045/4039050>.
            return KeyMessage("enter")
        elif key == ascii.SP:
            return KeyMessage("space")
        # TODO: check ctrl
        elif ascii.isalnum(key) or ascii.isspace(key):
            return KeyMessage(chr(key))
        else:
            return KeyMessage(f"key {key}")
