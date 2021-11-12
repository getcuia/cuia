"""An implementation of the renderer protocol using curses."""

from __future__ import annotations

import curses
from contextlib import contextmanager
from curses import ascii
from types import TracebackType
from typing import Callable, Iterator, Optional, Text, Type

from ..ansi import Parser
from ..ansi.token import Attr, Back, Fore, Ground
from ..color import BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW, Color
from ..message import Key, Message
from ._renderer import AbstractRenderer


def just(key: Key) -> Callable[[int], Key]:
    """Return a function that returns the given key when called."""
    return lambda _: key


def equal(key: int) -> Callable[[int], bool]:
    """Return a function that returns True when called with the given key."""
    return lambda k: k == key


RULES: list[tuple[Callable[[int], bool], Callable[[int], Message]]] = [
    (lambda key: key == curses.KEY_UP, lambda _: KeyMessage("up")),
    (lambda key: key == curses.KEY_DOWN, lambda _: KeyMessage("down")),
    (lambda key: key == curses.KEY_LEFT, lambda _: KeyMessage("left")),
    (lambda key: key == curses.KEY_RIGHT, lambda _: KeyMessage("right")),
    (lambda key: key == curses.KEY_HOME, lambda _: KeyMessage("home")),
    (lambda key: key == curses.KEY_END, lambda _: KeyMessage("end")),
    (lambda key: key == curses.KEY_PPAGE, lambda _: KeyMessage("pageup")),
    (lambda key: key == curses.KEY_NPAGE, lambda _: KeyMessage("pagedown")),
    (lambda key: key == curses.KEY_BACKSPACE, lambda _: KeyMessage("backspace")),
    (lambda key: key == curses.KEY_DC, lambda _: KeyMessage("delete")),
    (lambda key: key == curses.KEY_F1, lambda _: KeyMessage("f1")),
    (lambda key: key == curses.KEY_F2, lambda _: KeyMessage("f2")),
    (lambda key: key == curses.KEY_F3, lambda _: KeyMessage("f3")),
    (lambda key: key == curses.KEY_F4, lambda _: KeyMessage("f4")),
    (lambda key: key == curses.KEY_F5, lambda _: KeyMessage("f5")),
    (lambda key: key == curses.KEY_F6, lambda _: KeyMessage("f6")),
    (lambda key: key == curses.KEY_F7, lambda _: KeyMessage("f7")),
    (lambda key: key == curses.KEY_F8, lambda _: KeyMessage("f8")),
    (lambda key: key == curses.KEY_F9, lambda _: KeyMessage("f9")),
    (lambda key: key == curses.KEY_F10, lambda _: KeyMessage("f10")),
    (lambda key: key == curses.KEY_F11, lambda _: KeyMessage("f11")),
    # KEY_ENTER is rather unreliable, so we also accept ascii.LF
    # and ascii.CR.
    # See <https://stackoverflow.com/a/32255045/4039050>.
    (
        lambda key: key in {curses.KEY_ENTER, ascii.LF, ascii.CR},
        lambda _: KeyMessage("enter"),
    ),
    # (lambda key: key == curses.KEY_RESIZE, lambda _: KeyMessage("resize")),
    (lambda key: key == ascii.BEL, lambda _: KeyMessage("bell")),
    (lambda key: key == ascii.BS, lambda _: KeyMessage("backspace")),
    (lambda key: key == ascii.CAN, lambda _: KeyMessage("can")),
    (lambda key: key == ascii.DEL, lambda _: KeyMessage("delete")),
    (lambda key: key == ascii.EM, lambda _: KeyMessage("em")),
    (lambda key: key == ascii.ESC, lambda _: KeyMessage("escape")),
    (lambda key: key == ascii.ETB, lambda _: KeyMessage("etb")),
    (lambda key: key == ascii.FF, lambda _: KeyMessage("formfeed")),
    (lambda key: key == ascii.FS, lambda _: KeyMessage("fs")),
    (lambda key: key == ascii.GS, lambda _: KeyMessage("gs")),
    (lambda key: key == ascii.NAK, lambda _: KeyMessage("nak")),
    (lambda key: key == ascii.NL, lambda _: KeyMessage("newline")),
    (lambda key: key == ascii.RS, lambda _: KeyMessage("rs")),
    (lambda key: key == ascii.SI, lambda _: KeyMessage("shiftin")),
    (lambda key: key == ascii.SO, lambda _: KeyMessage("shiftout")),
    (lambda key: key == ascii.SP, lambda _: KeyMessage("space")),
    (lambda key: key == ascii.SUB, lambda _: KeyMessage("sub")),
    (lambda key: key == ascii.SYN, lambda _: KeyMessage("syn")),
    (lambda key: key == ascii.TAB, lambda _: KeyMessage("tab")),
    (lambda key: key == ascii.US, lambda _: KeyMessage("us")),
    (lambda key: key == ascii.VT, lambda _: KeyMessage("verticaltab")),
    (
        lambda key: ascii.isalnum(key) or ascii.isspace(key),
        lambda key: KeyMessage(chr(key)),
    ),
    (ascii.isctrl, lambda key: KeyMessage(f"ctrl+{chr(ord('a') - 1 + key)}")),
]


class Renderer(AbstractRenderer):
    """
    Curses renderer.

    Examples
    --------
    >>> with Renderer() as renderer:  # doctest: +SKIP
    ...     renderer.render("Hello, world!")
    """

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
        for hue in (None, BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE):
            self._init_color(hue)
        for foreground, background in ((None, None), (WHITE, BLACK)):
            self._init_color_pair(foreground, background)

    def __enter__(self) -> Renderer:
        """Enter context."""
        self._stdscr.keypad(True)
        self._stdscr.nodelay(True)
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context."""
        self._stdscr.nodelay(False)
        self._stdscr.keypad(False)
        curses.endwin()
        return None

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

    def _get_color_index(self, hue: Ground) -> int:
        """
        Translate color.

        This returns the appropriate curses color pair based on the new color and the
        kept state.
        """
        if isinstance(hue, Fore):
            self.foreground = hue.color
        elif isinstance(hue, Back):
            self.background = hue.color

        self._init_color(self.foreground)
        self._init_color(self.background)

        self._init_color_pair(self.foreground, self.background)
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

    def _init_color_pair(
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
                try:
                    self._stdscr.addstr(piece)
                except curses.error:
                    pass
            elif piece == Attr.NORMAL:
                self._reset_attributes()
            elif isinstance(piece, Attr):
                curses_attr = self._translate_attribute(piece)
                self._stdscr.attron(curses_attr)
            elif isinstance(piece, Ground):
                curses_attr = self._get_color_index(piece)
                self._stdscr.attron(curses_attr)
            # Silently ignore other pieces because they are probably unparsed Tokens.
        self._stdscr.noutrefresh()
        curses.doupdate()

    def next_message(self) -> Optional[Message]:
        """Get next message."""
        if (key := self._stdscr.getch()) == curses.ERR:
            return None

        for isvalid, translate in RULES:
            if isvalid(key):
                return translate(key)

        raise ValueError(f"unknown key: {key}")
