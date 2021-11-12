"""
Representation of ANSI escape sequences.

The token is the hub of all things ANSI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator, Text, Type

from kay import color
from kay.attr import Attr
from kay.color import Color, ground
from kay.misc import isplit

PATTERN = re.compile(r"(\N{ESC}\[[\d;]*[a-zA-Z])")
SEPARATOR = re.compile(r";")


GROUNDS = {
    # Foregrounds
    30: ground.Fore(color.BLACK),
    31: ground.Fore(color.RED),
    32: ground.Fore(color.GREEN),
    33: ground.Fore(color.YELLOW),
    34: ground.Fore(color.BLUE),
    35: ground.Fore(color.MAGENTA),
    36: ground.Fore(color.CYAN),
    37: ground.Fore(color.WHITE),
    # Backgrounds
    40: ground.Back(color.BLACK),
    41: ground.Back(color.RED),
    42: ground.Back(color.GREEN),
    43: ground.Back(color.YELLOW),
    44: ground.Back(color.BLUE),
    45: ground.Back(color.MAGENTA),
    46: ground.Back(color.CYAN),
    47: ground.Back(color.WHITE),
}


@dataclass(frozen=True)
class Token:
    """
    A token is a single ANSI escape.

    A complete ANSI escape sequence can require multiple tokens.
    This object is used as a representation of the ANSI escape sequence "language": we
    can make properties into tokens, and we can make strings into tokens.
    Furthermore, by having a token, we can make them into compact strings.
    """

    kind: Text
    data: int

    def issgr(self) -> bool:
        """
        Return True if this is a SGR escape sequence.

        Examples
        --------
        >>> Token(kind="m", data=0).issgr()
        True
        >>> Token(kind="H", data=0).issgr()
        False
        """
        return self.kind == "m"


def tokenize(text: Text) -> Iterable[Text | Token]:
    r"""
    Tokenize ANSI escape sequences from a string.

    This yields strings and escape sequences in the order they appear in the input.

    Examples
    --------
    >>> text = "I say: \x1b[38;2;0;255;0mhello, green!\x1b[m"
    >>> list(tokenize(text))  # doctest: +NORMALIZE_WHITESPACE
    ['I say: ',
    Token(kind='m', data=38),
    Token(kind='m', data=2),
    Token(kind='m', data=0),
    Token(kind='m', data=255),
    Token(kind='m', data=0),
    'hello, green!',
    Token(kind='m', data=0)]
    """
    for piece in isplit(PATTERN, text, include_separators=True):
        if piece:
            yield from parse(piece)


def parse(text: Text) -> Iterable[Text | Token]:
    r"""
    Parse a string into tokens if possible, otherwise yield the string as-is.

    Examples
    --------
    >>> list(parse("\033[m"))
    [Token(kind='m', data=0)]
    >>> list(parse("\x1b[1;31m"))
    [Token(kind='m', data=1), Token(kind='m', data=31)]
    >>> list(parse("\x1b[38;2;30;60;90m"))  # doctest: +NORMALIZE_WHITESPACE
    [Token(kind='m', data=38),
        Token(kind='m', data=2),
        Token(kind='m', data=30),
        Token(kind='m', data=60),
        Token(kind='m', data=90)]
    """
    if not text.startswith("\N{ESC}["):
        yield text
    else:
        kind = text[-1]
        if params := text[2:-1]:
            for param in isplit(SEPARATOR, params):
                yield Token(kind=kind, data=int(param))
        else:
            yield Token(kind=kind, data=0)


def escape(ts: Token | Iterable[Token]) -> Text:
    r"""
    Return a compact ANSI escape sequence for the given token or tokens.

    Examples
    --------
    >>> escape(Token(kind="m", data=1))
    '\x1b[1m'
    >>> escape([Token(kind="m", data=38),
    ...         Token(kind="m", data=2),
    ...         Token(kind="m", data=255),
    ...         Token(kind="m", data=0),
    ...         Token(kind="m", data=0)])
    '\x1b[38;2;255;;m'
    >>> escape([Token(kind="m", data=1), Token(kind="H", data=0)])
    '\x1b[1m\x1b[H'
    """

    def _escape(kind: Text, data: int | Text) -> Text:
        return f"\N{ESC}[{data or ''}{kind}"

    if isinstance(ts, Token):
        return _escape(ts.kind, ts.data)

    # TODO: call encode(...) automatically if not a token using a map, but wait
    # for encode to stabilize
    #
    # tokens = map(encode, tokens)

    # TODO: make a fold/reduce
    first, *rest = ts
    res = _escape(first.kind, first.data)[:-1]
    kind = first.kind
    for token in rest:
        if token.kind == kind:
            res += f";{token.data or ''}"
        else:
            res += f"{kind}{_escape(token.kind, token.data)[:-1]}"
            kind = token.kind
    return f"{res}{kind}"


def decode(ts: Iterable[Token]) -> Iterable[Attr | ground.Ground | Token]:
    """
    Decode a string of tokens into objects if possible, otherwise yield the token as-is.

    Examples
    --------
    >>> list(decode([Token(kind="m", data=1)]))
    [<Attr.BOLD: 1>]
    >>> list(decode([Token(kind="m", data=31)]))
    [Fore(color=Color(red=1.0, green=0.5826106699754192, blue=0.5805635742506021))]
    """
    if not isinstance(ts, Iterator):
        ts = iter(ts)
    while t := next(ts, None):
        if t.issgr():
            # TODO: use a dispatch table instead of a switch-like construct.
            if t.data < 30 or 50 <= t.data < 76:
                # Parse an SGR attribute token
                try:
                    yield Attr(t.data)
                except ValueError:
                    yield t
            elif 30 <= t.data < 50 or 90 <= t.data < 108:

                def _rgb(
                    t: Token, ts: Iterable[Token], cls: Type[ground.Ground]
                ) -> Iterable[Token | ground.Ground]:
                    """Parse an RGB color."""
                    if not isinstance(ts, Iterator):
                        ts = iter(ts)
                    bits = next(ts)
                    if isinstance(bits, Token) and bits.data == 2:
                        # 24-bit RGB color

                        red, green, blue = (next(ts), next(ts), next(ts))
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
                        yield t
                        yield bits

                if t.data in GROUNDS:
                    yield GROUNDS[t.data]
                elif t.data == 38:
                    yield from _rgb(t, ts, ground.Fore)
                elif t.data == 48:
                    yield from _rgb(t, ts, ground.Back)
                else:
                    yield t
            else:
                yield t
        else:
            # We currently don't support any other escape sequences.
            yield t


def encode(data: Attr | ground.Ground | Token | Iterable[Token]) -> Iterable[Token]:
    """
    Encode an Attr into a Token.

    Examples
    --------
    >>> list(encode(Attr.BOLD))
    [Token(kind='m', data=1)]
    >>> list(encode(encode(Attr.BOLD))) == list(encode(Attr.BOLD))
    True
    """
    # TODO: dispatch table!
    if isinstance(data, Attr):
        yield Token(kind="m", data=data.value)
    if isinstance(data, ground.Ground):
        base = 40 if isinstance(data, ground.Back) else 30
        if data.color == color.BLACK:
            yield Token(kind="m", data=base)
        elif data.color == color.RED:
            yield Token(kind="m", data=base + 1)
        elif data.color == color.GREEN:
            yield Token(kind="m", data=base + 2)
        elif data.color == color.YELLOW:
            yield Token(kind="m", data=base + 3)
        elif data.color == color.BLUE:
            yield Token(kind="m", data=base + 4)
        elif data.color == color.MAGENTA:
            yield Token(kind="m", data=base + 5)
        elif data.color == color.CYAN:
            yield Token(kind="m", data=base + 6)
        elif data.color == color.WHITE:
            yield Token(kind="m", data=base + 7)
        else:
            yield Token(kind="m", data=base + 8)
            yield Token(kind="m", data=2)

            red, green, blue = data.color.tobytes()
            yield Token(kind="m", data=red)
            yield Token(kind="m", data=green)
            yield Token(kind="m", data=blue)
    if isinstance(data, Token):
        yield data
    if isinstance(data, Iterable):
        yield from data
