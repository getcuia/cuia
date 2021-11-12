"""Facilities for working with text style attributes."""

from __future__ import annotations

from enum import Enum

from kay import ansi


class Attr(Enum):
    r"""
    ANSI escape sequence text style attributes.

    Examples
    --------
    >>> Attr.BOLD
    <Attr.BOLD: 1>
    >>> from kay.ansi import escape, token
    >>> list(token.encode(Attr.BOLD))
    [Token(kind='m', data=1)]
    >>> escape(token.encode(Attr.BOLD))
    '\x1b[1m'
    """

    NORMAL = 0
    BOLD = 1
    FAINT = 2
    # ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    #
    REVERSE = 7

    def __str__(self) -> str:
        """Return the ANSI escape sequence for this attribute."""
        return ansi.escape(ansi.token.encode(self))
