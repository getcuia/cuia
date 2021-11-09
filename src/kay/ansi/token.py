"""Representation of ANSI escape sequences."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Text

from kay.ansi import isplit

SEPARATOR = re.compile(r";")


@dataclass(frozen=True)
class Token:
    """A token is a single ANSI escape sequence."""

    group: Text
    data: int

    def issgr(self) -> bool:
        """Return True if this is a SGR escape sequence."""
        return self.group == "m"

    def __str__(self) -> Text:
        """Return a string representation of this token."""
        return f"\N{ESC}[{self.data}{self.group}"

    @staticmethod
    def fromstring(text: Text) -> Iterable[Text | Token]:
        r"""
        Create tokens from a string or return it.

        Examples
        --------
        >>> list(Token.fromstring("\033[m"))
        [Token(group='m', data=0)]
        >>> list(Token.fromstring("\x1b[1;31m"))
        [Token(group='m', data=1), Token(group='m', data=31)]
        >>> list(Token.fromstring("\x1b[38;2;30;60;90m"))  # doctest: +NORMALIZE_WHITESPACE
        [Token(group='m', data=38),
         Token(group='m', data=2),
         Token(group='m', data=30),
         Token(group='m', data=60),
         Token(group='m', data=90)]
        """
        if not text.startswith("\N{ESC}["):
            yield text
        else:
            marker = text[-1]
            if params := text[2:-1]:
                for param in isplit(SEPARATOR, params):
                    yield Token(group=marker, data=int(param))
            else:
                yield Token(group=marker, data=0)
