"""An implementation of the renderer protocol using curses."""

from __future__ import annotations

import asyncio
import curses
from contextlib import contextmanager
from curses import ascii
from typing import Iterator, Optional, Text

from kay import ansi, color
from kay.attr import Attr
from kay.color import Background, Color, Foreground
from kay.message import KeyMessage, Message
from kay.renderer import Renderer


class CursesRenderer(Renderer):
    """Curses renderer."""

    _stdscr: curses._CursesWindow
    foreground: Optional[Color] = None
    background: Optional[Color] = None
    colors: dict[Optional[Color], int] = {}
    color_pairs: dict[tuple[Optional[Color], Optional[Color]], int] = {}

    def __init__(self) -> None:
        """Initialize."""
        self._stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        # More:
        # https://github.com/gyscos/cursive/blob/c4c74c02996f3f6e66136b51a4d83d2562af740a/cursive/src/backends/curses/n.rs#L133-L143
        for hue in (
            None,
            color.BLACK,
            color.RED,
            color.GREEN,
            color.YELLOW,
            color.BLUE,
            color.MAGENTA,
            color.CYAN,
            color.WHITE,
        ):
            self._init_color(hue)
        for foreground, background in ((None, None), (color.WHITE, color.BLACK)):
            self._init_pair(foreground, background)

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
        elif isinstance(color, Background):
            self.background = color.color

        self._init_color(self.foreground)
        self._init_color(self.background)

        self._init_pair(self.foreground, self.background)
        return curses.color_pair(self.color_pairs[(self.foreground, self.background)])

    def _init_color(self, color: Optional[Color], n: Optional[int] = None) -> None:
        """
        Initialize color.

        This initializes the color if it is not yet initialized.
        """
        if color not in self.colors:
            self.colors[color] = n or len(self.colors) - 1
            if color is not None:
                r, g, b = color
                r = r * 1000 // 255
                g = g * 1000 // 255
                b = b * 1000 // 255
                curses.init_color(self.colors[color], r, g, b)

    def _init_pair(
        self,
        foreground: Optional[Color],
        background: Optional[Color],
        n: Optional[int] = None,
    ) -> None:
        """
        Initialize color pair.

        This initializes the color pair if it is not yet initialized.
        """
        if (foreground, background) not in self.color_pairs:
            self.color_pairs[(foreground, background)] = n or len(self.color_pairs) - 1
            if (foreground, background) != (None, None):
                curses.init_pair(
                    self.color_pairs[(foreground, background)],
                    self.colors[foreground],
                    self.colors[background],
                )

    # TODO: this does not seem to need to be a coroutine
    async def render(self, view: Text) -> None:
        """Render model."""
        await asyncio.sleep(1 / 120)
        self._stdscr.erase()
        self._reset_attributes()
        for piece in ansi.parse(view):
            if isinstance(piece, Text):
                self._stdscr.addstr(piece)
            elif piece == Attr.NORMAL:
                self._reset_attributes()
            elif isinstance(piece, Attr):
                curses_attr = self._translate_attribute(piece)
                self._stdscr.attron(curses_attr)
            else:
                curses_attr = self._translate_color(piece)
                self._stdscr.attron(curses_attr)
        self._stdscr.noutrefresh()
        curses.doupdate()

    # TODO: this does not seem to need to be a coroutine
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
