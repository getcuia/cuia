"""Facilities for working with attributes."""

from __future__ import annotations

from enum import Enum
from typing import Text

from kay.ansi.token import Token


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

    def token(self) -> Token:
        """Return a Token with this attribute."""
        return Token(group="m", data=self.value)

    def __str__(self) -> Text:
        """Return the ANSI escape sequence for this attribute."""
        return Text(self.token())
