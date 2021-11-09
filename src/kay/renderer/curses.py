"""An implementation of the renderer protocol using curses."""

from __future__ import annotations

import curses
from contextlib import contextmanager
from curses import ascii
from typing import Iterator, Optional, Text

from kay import color, renderer
from kay.ansi.parser import Parser
from kay.attr import Attr
from kay.color import Background, Color, Foreground
from kay.message import KeyMessage, Message


class Renderer(renderer.Renderer):
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
        # https://github.com/gyscos/cursive/blob/c4c74c02996f3f6e66136b51a4d83d2562af740a/cursive/src/backends/curses/n.rs#L137-L143
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

    def __enter__(self) -> Renderer:
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
    def into_raw_mode(self) -> Iterator[Renderer]:
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

    def _translate_color(self, hue: Foreground | Background) -> int:
        """
        Translate color.

        This returns the appropriate curses color pair based on the new color and the
        kept state.
        """
        if isinstance(hue, Foreground):
            self.foreground = hue.color
        elif isinstance(hue, Background):
            self.background = hue.color

        self._init_color(self.foreground)
        self._init_color(self.background)

        self._init_pair(self.foreground, self.background)
        return curses.color_pair(self.color_pairs[(self.foreground, self.background)])

    def _init_color(self, hue: Optional[Color], id: Optional[int] = None) -> None:
        """
        Initialize color.

        This initializes the color if it is not yet initialized.
        """
        if hue not in self.colors:
            self.colors[hue] = id or len(self.colors) - 1
            if hue is not None:
                red, green, blue = hue
                red = int(red * 1000)
                green = int(green * 1000)
                blue = int(blue * 1000)
                curses.init_color(self.colors[hue], red, green, blue)

    def _init_pair(
        self,
        foreground: Optional[Color],
        background: Optional[Color],
        id: Optional[int] = None,
    ) -> None:
        """
        Initialize color pair.

        This initializes the color pair if it is not yet initialized.
        """
        if (foreground, background) not in self.color_pairs:
            self.color_pairs[(foreground, background)] = id or len(self.color_pairs) - 1
            if (foreground, background) != (None, None):
                curses.init_pair(
                    self.color_pairs[(foreground, background)],
                    self.colors[foreground],
                    self.colors[background],
                )

    def render(self, view: Text) -> None:
        """Render model."""
        self._stdscr.erase()
        self._reset_attributes()
        parser = Parser()
        parser.tokenize(view)
        for piece in parser.parse():
            if isinstance(piece, Text):
                self._stdscr.addstr(piece)
            elif piece == Attr.NORMAL:
                self._reset_attributes()
            elif isinstance(piece, Attr):
                curses_attr = self._translate_attribute(piece)
                self._stdscr.attron(curses_attr)
            elif isinstance(piece, (Foreground, Background)):
                curses_attr = self._translate_color(piece)
                self._stdscr.attron(curses_attr)
            # Silently ignore other pieces because they are probably unparsed Tokens.
        self._stdscr.noutrefresh()
        curses.doupdate()

    def next_message(self) -> Optional[Message]:
        """Get next message."""
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
