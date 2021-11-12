"""
A simple ANSI escape sequence parser.

Only a subset of the ANSI escape sequences are supported, namely a subset of
the SGR (Select Graphic Rendition) escape sequences.

This performs [lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis) in
general.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Text

from kay.ansi import token
from kay.attr import Attr
from kay.color import ground


@dataclass
class Parser:
    """A parser for ANSI escape sequences."""

    tokens: Optional[Iterator[Text | token.Token]] = None

    def tokenize(self, text: Text) -> None:
        r"""
        Tokenize ANSI escape sequences in a string and store them in the parser.

        Examples
        --------
        >>> p = Parser()
        >>> p.tokenize("\x1B[38;2;0;255;0mHello, green!\x1b[m")
        """
        self.tokens = token.tokenize(text)

    def parse(self) -> Iterable[Text | token.Token | Attr | ground.Ground]:
        r"""
        Parse ANSI escape sequences from a string.

        This yields strings and attributes in order they appear in the input.
        Only a subset of the ANSI escape sequences are supported, namely a subset of
        the SGR (Select Graphic Rendition) escape sequences.
        If an escape sequence is not supported, it is yielded separately as a
        non-parsed Token.

        A SGR escape sequence is a sequence that starts with an Control Sequence
        Introducer (CSI) and ends with an `m`.
        A CSI escape sequence is a sequence that starts with an escape character
        (`\033` or `\x1B`) followed by an opening bracket (`[` or `\x5B`).

        Examples
        --------
        >>> p = Parser()
        >>> p.tokenize(
        ...     "\N{ESC}[0;38;2;255;0;0mHello\x1b[m, "
        ...     "\x1B[1;38;2;0;255;0mWorld!\N{ESC}[0m"
        ... )
        >>> for code in p.parse():
        ...     code  # doctest: +NORMALIZE_WHITESPACE
        <Attr.NORMAL: 0>
        Fore(color=Color(red=1.0, green=0.0, blue=0.0))
        'Hello'
        <Attr.NORMAL: 0>
        ', '
        <Attr.BOLD: 1>
        Fore(color=Color(red=0.0, green=1.0, blue=0.0))
        'World!'
        <Attr.NORMAL: 0>

        You can use the same parser object more than once:

        >>> p.tokenize("\x1B[38;2;0;255;0mHello, green!\x1b[m")
        >>> for code in p.parse():
        ...     code
        Fore(color=Color(red=0.0, green=1.0, blue=0.0))
        'Hello, green!'
        <Attr.NORMAL: 0>
        """
        if self.tokens is None:
            raise RuntimeError(
                "Parser has not been tokenized. "
                "tokenize() must be called before parse()"
            )

        ts: list[token.Token] = []
        while t := next(self.tokens, None):
            if isinstance(t, token.Token):
                ts.append(t)
            else:
                if ts:
                    yield from token.decode(ts)
                    ts.clear()

                yield t

        if ts:
            yield from token.decode(ts)


if __name__ == "__main__":
    p = Parser()
    p.tokenize("\N{ESC}[0;31mHello\x1b[m, \x1B[1;32mWorld!\N{ESC}[0m")
    for x in p.parse():
        print(repr(x))
