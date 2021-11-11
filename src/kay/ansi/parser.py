"""
A simple ANSI escape sequence parser.

Only a subset of the ANSI escape sequences are supported, namely a subset of
the SGR (Select Graphic Rendition) escape sequences.

This performs [lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis) in
general.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Text, Type

from kay.ansi import PATTERN
from kay.ansi.token import Token
from kay.attr import Attr
from kay.color import Background, Color, Foreground
from kay.misc import isplit


@dataclass
class Parser:
    """A parser for ANSI escape sequences."""

    tokens: Optional[Iterator[Text | Token]] = None

    def tokenize(self, text: Text) -> None:
        """Tokenize ANSI escape sequences in a string and store them in the parser."""
        self.tokens = Parser._tokenize(text)

    def parse(self) -> Iterable[Text | Token | Attr | Foreground | Background]:
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
        >>> p.tokenize(f"\N{ESC}[0;38;2;255;0;0mHello\x1b[m, \x1B[1;38;2;0;255;0mWorld!\N{ESC}[0m")
        >>> for code in p.parse():
        ...     code  # doctest: +NORMALIZE_WHITESPACE
        <Attr.NORMAL: 0>
        Foreground(color=Color(red=1.0, green=0.0, blue=0.0))
        'Hello'
        <Attr.NORMAL: 0>
        ', '
        <Attr.BOLD: 1>
        Foreground(color=Color(red=0.0, green=1.0, blue=0.0))
        'World!'
        <Attr.NORMAL: 0>

        You can use the same parser object more than once:

        >>> p.tokenize("\x1B[38;2;0;255;0mHello, green!\x1b[m")
        >>> for code in p.parse():
        ...     code
        Foreground(color=Color(red=0.0, green=1.0, blue=0.0))
        'Hello, green!'
        <Attr.NORMAL: 0>
        """
        if self.tokens is None:
            raise RuntimeError(
                "Parser has not been tokenized. "
                "tokenize() must be called before parse()"
            )

        while token := next(self.tokens, None):
            if isinstance(token, Token):
                yield from self._parse_token(token)
            else:
                yield token

    def _parse_token(
        self, token: Token
    ) -> Iterable[Text | Token | Attr | Foreground | Background]:
        """Parse a single token."""
        if token.issgr():
            yield from self._parse_token_sgr(token)
        # We currently don't support any other escape sequences.
        else:
            yield token

    def _parse_token_sgr(
        self, token: Token
    ) -> Iterable[Text | Token | Attr | Foreground | Background]:
        """Parse a SGR token."""
        if token.data < 30 or 50 <= token.data < 76:
            # Parse an SGR attribute token
            try:
                yield Attr(token.data)
            except ValueError:
                yield token
        elif 30 <= token.data < 50 or 90 <= token.data < 108:
            yield from self._parse_token_sgr_color(token)
        else:
            yield token

    def _parse_token_sgr_color(
        self, token: Token
    ) -> Iterable[Text | Token | Foreground | Background]:
        """Parse an SGR color token."""

        def _rgb(
            cls: Type[Foreground | Background],
        ) -> Iterable[Text | Token | Foreground | Background]:
            """Parse an RGB color."""
            assert self.tokens is not None, "Parser has no tokens"

            bits = next(self.tokens)
            if isinstance(bits, Token) and bits.data == 2:
                # 24-bit RGB color

                red, green, blue = (
                    next(self.tokens),
                    next(self.tokens),
                    next(self.tokens),
                )
                if not (
                    isinstance(red, Token)
                    and isinstance(green, Token)
                    and isinstance(blue, Token)
                ):
                    raise ValueError(
                        f"Expected three numbers after {cls.__name__} "
                        f"but got {red}, {green}, {blue}"
                    )

                yield cls(Color.frombytes(red.data, green.data, blue.data))
            else:
                # Send them back, we don't support 256-color mode yet (and we might
                # never do).
                yield token
                yield bits

        if 30 <= token.data < 38:
            yield Foreground(Color.fromint(token.data))
        elif 40 <= token.data < 48:
            yield Background(Color.fromint(token.data))
        elif token.data == 38:
            yield from _rgb(Foreground)
        elif token.data == 48:
            yield from _rgb(Background)
        else:
            yield token

    @staticmethod
    def _tokenize(text: Text) -> Iterator[Text | Token]:
        r"""
        Tokenize ANSI escape sequences from a string.

        This yields strings and escape sequences in order they appear in the input.

        Examples
        --------
        >>> list(
        ...     Parser._tokenize("\x1b[38;2;0;255;0mHello, green!\x1b[m")
        ... )  # doctest: +NORMALIZE_WHITESPACE
        [Token(kind='m', data=38),
        Token(kind='m', data=2),
        Token(kind='m', data=0),
        Token(kind='m', data=255),
        Token(kind='m', data=0),
        'Hello, green!',
        Token(kind='m', data=0)]
        """
        for piece in isplit(PATTERN, text, include_separators=True):
            if piece:
                yield from Token.decode(piece)


if __name__ == "__main__":
    p = Parser()
    p.tokenize("\N{ESC}[0;31mHello\x1b[m, \x1B[1;32mWorld!\N{ESC}[0m")
    for x in p.parse():
        print(repr(x))
