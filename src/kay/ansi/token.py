"""
Representation of ANSI escape sequences.

The token is the hub of all things ANSI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Text

from kay.attr import Attr
from kay.misc import isplit

SEPARATOR = re.compile(r";")


@dataclass(frozen=True)
class Token:
    """
    A token is a single ANSI escape.

    A complete ANSI escape sequence can require multiple tokens.
    This object is used as a representation of the ANSI escape sequence "language": we
    can encode properties into tokens, and we can decode strings into tokens.
    Furthermore, by having a token, we can transform them into compact strings.
    """

    kind: Text
    data: int

    def issgr(self) -> bool:
        """Return True if this is a SGR escape sequence."""
        return self.kind == "m"

    @staticmethod
    def decode(text: Text) -> Iterable[Text | Token]:
        r"""
        Decode a string into tokens if possible, otherwise yield the unknown parts.

        Examples
        --------
        >>> list(Token.decode("\033[m"))
        [Token(kind='m', data=0)]
        >>> list(Token.decode("\x1b[1;31m"))
        [Token(kind='m', data=1), Token(kind='m', data=31)]
        >>> list(Token.decode("\x1b[38;2;30;60;90m"))  # doctest: +NORMALIZE_WHITESPACE
        [Token(kind='m', data=38),
         Token(kind='m', data=2),
         Token(kind='m', data=30),
         Token(kind='m', data=60),
         Token(kind='m', data=90)]
        """
        if not text.startswith("\N{ESC}["):
            yield text
        else:
            marker = text[-1]
            if params := text[2:-1]:
                for param in isplit(SEPARATOR, params):
                    yield Token(kind=marker, data=int(param))
            else:
                yield Token(kind=marker, data=0)
