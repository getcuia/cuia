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
    # Minimum key value
    (equal(curses.KEY_MIN), just(Key("min"))),
    # Break key (unreliable)
    (equal(curses.KEY_BREAK), just(Key("break"))),
    # Down-arrow
    (equal(curses.KEY_DOWN), just(Key("down"))),
    # Up-arrow
    (equal(curses.KEY_UP), just(Key("up"))),
    # Left-arrow
    (equal(curses.KEY_LEFT), just(Key("left"))),
    # Right-arrow
    (equal(curses.KEY_RIGHT), just(Key("right"))),
    # Home key (upward+left arrow)
    (equal(curses.KEY_HOME), just(Key("home"))),
    # Backspace (unreliable)
    (equal(curses.KEY_BACKSPACE), just(Key("backspace"))),
    # Function keys. Up to 64 function keys are supported.
    (
        lambda key: curses.KEY_F0 <= key <= curses.KEY_F63,
        lambda key: Key(f"f{key - curses.KEY_F0}"),
    ),
    # Delete line
    (equal(curses.KEY_DL), just(Key("dl"))),
    # Insert line
    (equal(curses.KEY_IL), just(Key("il"))),
    # Delete character
    (equal(curses.KEY_DC), just(Key("delete"))),
    # Insert char or enter insert mode
    (equal(curses.KEY_IC), just(Key("ic"))),
    # Exit insert char mode
    (equal(curses.KEY_EIC), just(Key("eic"))),
    # Clear screen
    (equal(curses.KEY_CLEAR), just(Key("clear"))),
    # Clear to end of screen
    (equal(curses.KEY_EOS), just(Key("eos"))),
    # Clear to end of line
    (equal(curses.KEY_EOL), just(Key("eol"))),
    # Scroll 1 line forward
    (equal(curses.KEY_SF), just(Key("sf"))),
    # Scroll 1 line backward (reverse)
    (equal(curses.KEY_SR), just(Key("sr"))),
    # Next page
    (equal(curses.KEY_NPAGE), just(Key("pagedown"))),
    # Previous page
    (equal(curses.KEY_PPAGE), just(Key("pageup"))),
    # Set tab
    (equal(curses.KEY_STAB), just(Key("stab"))),
    # Clear tab
    (equal(curses.KEY_CTAB), just(Key("ctab"))),
    # Clear all tabs
    (equal(curses.KEY_CATAB), just(Key("catab"))),
    # Soft (partial) reset (unreliable)
    (equal(curses.KEY_SRESET), just(Key("sreset"))),
    # Reset or hard reset (unreliable)
    (equal(curses.KEY_RESET), just(Key("reset"))),
    # Print
    (equal(curses.KEY_PRINT), just(Key("print"))),
    # Home down or bottom (lower left)
    (equal(curses.KEY_LL), just(Key("ll"))),
    # Upper left of keypad
    (equal(curses.KEY_A1), just(Key("a1"))),
    # Upper right of keypad
    (equal(curses.KEY_A3), just(Key("a3"))),
    # Center of keypad
    (equal(curses.KEY_B2), just(Key("b2"))),
    # Lower left of keypad
    (equal(curses.KEY_C1), just(Key("c1"))),
    # Lower right of keypad
    (equal(curses.KEY_C3), just(Key("c3"))),
    # Back tab
    (equal(curses.KEY_BTAB), just(Key("btab"))),
    # Beg (beginning)
    (equal(curses.KEY_BEG), just(Key("beg"))),
    # Cancel
    (equal(curses.KEY_CANCEL), just(Key("cancel"))),
    # Close
    (equal(curses.KEY_CLOSE), just(Key("close"))),
    # Cmd (command)
    (equal(curses.KEY_COMMAND), just(Key("cmd"))),
    # Copy
    (equal(curses.KEY_COPY), just(Key("copy"))),
    # Create
    (equal(curses.KEY_CREATE), just(Key("create"))),
    # End
    (equal(curses.KEY_END), just(Key("end"))),
    # Exit
    (equal(curses.KEY_EXIT), just(Key("exit"))),
    # Find
    (equal(curses.KEY_FIND), just(Key("find"))),
    # Help
    (equal(curses.KEY_HELP), just(Key("help"))),
    # Mark
    (equal(curses.KEY_MARK), just(Key("mark"))),
    # Message
    (equal(curses.KEY_MESSAGE), just(Key("message"))),
    # Move
    (equal(curses.KEY_MOVE), just(Key("move"))),
    # Next
    (equal(curses.KEY_NEXT), just(Key("next"))),
    # Open
    (equal(curses.KEY_OPEN), just(Key("open"))),
    # Options
    (equal(curses.KEY_OPTIONS), just(Key("options"))),
    # Prev (previous)
    (equal(curses.KEY_PREVIOUS), just(Key("previous"))),
    # Redo
    (equal(curses.KEY_REDO), just(Key("redo"))),
    # Ref (reference)
    (equal(curses.KEY_REFERENCE), just(Key("reference"))),
    # Refresh
    (equal(curses.KEY_REFRESH), just(Key("refresh"))),
    # Replace
    (equal(curses.KEY_REPLACE), just(Key("replace"))),
    # Restart
    (equal(curses.KEY_RESTART), just(Key("restart"))),
    # Resume
    (equal(curses.KEY_RESUME), just(Key("resume"))),
    # Save
    (equal(curses.KEY_SAVE), just(Key("save"))),
    # Shifted Beg (beginning)
    (equal(curses.KEY_SBEG), just(Key("sbeg"))),
    # Shifted Cancel
    (equal(curses.KEY_SCANCEL), just(Key("scancel"))),
    # Shifted Command
    (equal(curses.KEY_SCOMMAND), just(Key("scommand"))),
    # Shifted Copy
    (equal(curses.KEY_SCOPY), just(Key("scopy"))),
    # Shifted Create
    (equal(curses.KEY_SCREATE), just(Key("screate"))),
    # Shifted Delete char
    (equal(curses.KEY_SDC), just(Key("sdc"))),
    # Shifted Delete line
    (equal(curses.KEY_SDL), just(Key("sdl"))),
    # Select
    (equal(curses.KEY_SELECT), just(Key("select"))),
    # Shifted End
    (equal(curses.KEY_SEND), just(Key("send"))),
    # Shifted Clear line
    (equal(curses.KEY_SEOL), just(Key("seol"))),
    # Shifted Exit
    (equal(curses.KEY_SEXIT), just(Key("sexit"))),
    # Shifted Find
    (equal(curses.KEY_SFIND), just(Key("sfind"))),
    # Shifted Help
    (equal(curses.KEY_SHELP), just(Key("shelp"))),
    # Shifted Home
    (equal(curses.KEY_SHOME), just(Key("shome"))),
    # Shifted Input
    (equal(curses.KEY_SIC), just(Key("sic"))),
    # Shifted Left arrow
    (equal(curses.KEY_SLEFT), just(Key("sleft"))),
    # Shifted Message
    (equal(curses.KEY_SMESSAGE), just(Key("shmemu"))),
    # Shifted Move
    (equal(curses.KEY_SMOVE), just(Key("shome"))),
    # Shifted Next
    (equal(curses.KEY_SNEXT), just(Key("s-next"))),
    # Shifted Options
    (equal(curses.KEY_SOPTIONS), just(Key("shift-f1"))),
    # Shifted Prev
    (equal(curses.KEY_SPREVIOUS), just(Key("shleft"))),
    # Shifted Print
    (equal(curses.KEY_SPRINT), just(Key("sprint"))),
    # Shifted Redo
    (equal(curses.KEY_SREDO), just(Key("sh redo"))),
    # Shifted Replace
    (equal(curses.KEY_SREPLACE), just(Key("sredo"))),
    # Shifted Right arrow
    (equal(curses.KEY_SRIGHT), just(Key("sright"))),
    # Shifted Resume
    (equal(curses.KEY_SRSUME), just(Key("shift_resume"))),
    # Shifted Save
    (equal(curses.KEY_SSAVE), just(Key("sbeg"))),
    # Shifted Suspend
    (equal(curses.KEY_SSUSPEND), just(Key("suspend"))),
    # Shifted Undo
    (equal(curses.KEY_SUNDO), just(Key("undo"))),
    # Suspend
    (equal(curses.KEY_SUSPEND), just(Key("suspend"))),
    # Undo
    (equal(curses.KEY_UNDO), just(Key("undo"))),
    # Mouse event has occurred
    (equal(curses.KEY_MOUSE), just(Key("mouse"))),
    # Terminal resize event
    (equal(curses.KEY_RESIZE), just(Key("resize"))),
    # Maximum key value
    (equal(curses.KEY_MAX), just(Key("max"))),
    # Enter or send (unreliable)
    (equal(curses.KEY_ENTER), just(Key("enter"))),
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
