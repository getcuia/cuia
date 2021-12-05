"""A renderer that uses Python's standard curses library."""

from __future__ import annotations

import curses
from contextlib import contextmanager
from curses import ascii
from dataclasses import dataclass, field
from types import TracebackType
from typing import Callable, Iterable, Iterator, Optional, Text, Type

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

        for isvalid, translate in RULES:
            if isvalid(key):
                return translate(key)

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


def always(key: int) -> bool:
    """Return True for any key."""
    return True


def equal(key: int) -> Callable[[int], bool]:
    """Return a function that returns True when called with the given key."""
    return lambda k: k == key


def either(fs: Iterable[Callable[[int], bool]]) -> Callable[[int], bool]:
    """Return a function that returns True when any of the given ones returns True."""
    fs = set(fs)
    return lambda k: any(f(k) for f in fs)


def just(key: Key) -> Callable[[int], Key]:
    """Return a function that returns the given key when called."""
    return lambda _: key


RULES: list[tuple[Callable[[int], bool], Callable[[int], Message]]] = [
    # Up-arrow
    (equal(curses.KEY_UP), just(Key("up"))),
    # Down-arrow
    (equal(curses.KEY_DOWN), just(Key("down"))),
    # Left-arrow
    (equal(curses.KEY_LEFT), just(Key("left"))),
    # Right-arrow
    (equal(curses.KEY_RIGHT), just(Key("right"))),
    # Function keys. Up to 64 function keys are supported.
    (
        either(equal(key) for key in range(curses.KEY_F0, curses.KEY_F63 + 1)),
        lambda key: Key(f"f{key - curses.KEY_F0}"),
    ),
    #
    # Insert char or enter insert mode
    (equal(curses.KEY_IC), just(Key("insert"))),
    # Delete character
    (either(equal(key) for key in {ascii.DEL, curses.KEY_DC}), just(Key("delete"))),
    # Home key (upward+left arrow)
    (equal(curses.KEY_HOME), just(Key("home"))),
    # End
    (equal(curses.KEY_END), just(Key("end"))),
    # Previous page
    (equal(curses.KEY_PPAGE), just(Key("pageup"))),
    # Next page
    (equal(curses.KEY_NPAGE), just(Key("pagedown"))),
    #
    # Delete line
    (equal(curses.KEY_DL), just(Key("dl"))),
    # Insert line
    (equal(curses.KEY_IL), just(Key("il"))),
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
    # Set tab
    (equal(curses.KEY_STAB), just(Key("stab"))),
    # Clear tab
    (equal(curses.KEY_CTAB), just(Key("ctab"))),
    # Clear all tabs
    (equal(curses.KEY_CATAB), just(Key("catab"))),
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
    # Minimum key value
    (equal(curses.KEY_MIN), just(Key("min"))),
    # Maximum key value
    (equal(curses.KEY_MAX), just(Key("max"))),
    #
    # Enter or send (unreliable, so we also accept carriage returns and line feeds .
    # See <https://stackoverflow.com/a/32255045/4039050>.
    (
        either(equal(key) for key in {ascii.CR, ascii.LF, curses.KEY_ENTER}),
        just(Key("enter")),
    ),
    #
    # Space bar
    (equal(ascii.SP), just(Key("space"))),
    #
    # Break key (unreliable)
    (equal(curses.KEY_BREAK), just(Key("break"))),
    # Backspace (unreliable)
    (
        either(equal(key) for key in {ascii.BS, curses.KEY_BACKSPACE}),
        just(Key("backspace")),
    ),
    # Soft (partial) reset (unreliable)
    (equal(curses.KEY_SRESET), just(Key("sreset"))),
    # Reset or hard reset (unreliable)
    (equal(curses.KEY_RESET), just(Key("reset"))),
    #
    # Escape key
    (equal(ascii.ESC), just(Key("escape"))),
    # Tab key
    (equal(ascii.TAB), just(Key("tab"))),
    #
    (ascii.isctrl, lambda key: Key(f"ctrl+{chr(ord('a') - 1 + key)}")),
    # Fallback
    (always, lambda key: Key(chr(key))),
]


