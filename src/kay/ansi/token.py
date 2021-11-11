"""Representation of ANSI escape sequences."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Text

from kay.misc import isplit

SEPARATOR = re.compile(r";")


@dataclass(frozen=True)
class Token:
    """A token is a single ANSI escape sequence."""

    kind: Text
    data: int

    def issgr(self) -> bool:
        """Return True if this is a SGR escape sequence."""
        return self.kind == "m"

    def __str__(self) -> Text:
        """Return a string representation of this token."""
        return f"\N{ESC}[{self.data}{self.kind}"

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
