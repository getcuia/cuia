"""Representation of ANSI escape sequences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Text


@dataclass(frozen=True)
class Token:
    """A token is a single ANSI escape sequence."""

    marker: Text
    param: int = 0

    def issgr(self) -> bool:
        """Return True if this is a SGR escape sequence."""
        return self.marker == "m"

    def __str__(self) -> Text:
        """Return a string representation of this token."""
        return f"\N{ESC}[{self.param}{self.marker}"

    @staticmethod
    def fromstring(text: Text) -> Iterable[Text | Token]:
        r"""
        Create tokens from a string or return it.

        Examples
        --------
        >>> list(Token.fromstring("\033[m"))
        [Token(marker='m', param=0)]
        >>> list(Token.fromstring("\x1b[1;31m"))
        [Token(marker='m', param=1), Token(marker='m', param=31)]
        >>> list(Token.fromstring("\x1b[38;2;30;60;90m"))  # doctest: +NORMALIZE_WHITESPACE
        [Token(marker='m', param=38),
         Token(marker='m', param=2),
         Token(marker='m', param=30),
         Token(marker='m', param=60),
         Token(marker='m', param=90)]
        """
        if not text.startswith("\N{ESC}["):
            yield text
        else:
            marker, params = text[-1], text[2:-1].split(";")
            for param in params:
                if param:
                    yield Token(marker=marker, param=int(param))
                else:
                    yield Token(marker=marker)
