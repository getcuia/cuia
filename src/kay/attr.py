"""Facilities for working with text style attributes."""

from __future__ import annotations

from enum import Enum
from typing import Text

from kay.ansi.token import Token


class Attr(Enum):
    r"""
    ANSI escape sequence text style attributes.

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
        """
        Return a ANSI Token with this text style attribute.

        Examples
        --------
        >>> Attr.BOLD.token()
        Token(group='m', data=1)
        """
        return Token(kind="m", data=self.value)

    def __str__(self) -> Text:
        """Return the ANSI escape sequence for this text style attribute."""
        return Text(self.token())
