"""Facilities for working with attributes."""

from __future__ import annotations

from enum import Enum
from typing import Text

ESC = "\033"
CSI = f"{ESC}["


class Attr(Enum):
    r"""
    ANSI escape sequence attributes.

    Examples
    --------
    >>> Attr.BOLD
    <Attr.BOLD: 1>
    >>> Text(Attr.BOLD)
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

    def __str__(self):
        """Return the ANSI escape sequence for this attribute."""
        return sgr(self.value)


def sgr(code: Text | int) -> Text:
    r"""
    Convert an SGR code to an ANSI escape sequence.

    Examples
    --------
    >>> sgr(1)
    '\x1b[1m'
    """
    return f"{CSI}{code}m"
