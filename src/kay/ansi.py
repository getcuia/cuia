"""
A simple ANSI escape sequence parser.

Only a subset of the ANSI escape sequences are supported, namely a subset of
the SGR (Select Graphic Rendition) escape sequences.
"""

from __future__ import annotations

import re
from typing import Iterable, Text

from kay.attr import CSI, Attr, sgr
from kay.color import Background, Color, Foreground

SGR_FORMAT = re.compile(rf"({CSI}[0-9;]*m)")


def parse(text: Text) -> Iterable[Text | Attr | Foreground | Background]:
    r"""
    Parse ANSI escape sequences from a string.

    This yields both strings and attributes in order they appear in the input.
    If an escape sequence is not supported, it is yielded separately as a string.

    Only a subset of the ANSI escape sequences are supported, namely a subset of
    the SGR (Select Graphic Rendition) escape sequences.

    A SGR escape sequence is a sequence that starts with an Control Sequence Introducer
    (CSI) and ends with an `m`.

    A CSI escape sequence is a sequence that starts with an escape character
    (`\033` or `\x1B`) followed by an opening bracket (`[` or `\x5B`).

    Examples
    --------
    >>> for code in parse(f"{CSI}0;31mHello\x1b[m, \x1B[1;32mWorld!{CSI}0m"):
    ...     code
    <Attr.NORMAL: 0>
    Color(red=179, green=16, blue=14)
    'Hello'
    <Attr.NORMAL: 0>
    ', '
    <Attr.BOLD: 1>
    Color(red=11, green=172, blue=22)
    'World!'
    <Attr.NORMAL: 0>
    >>> for code in parse("\x1B[38;2;0;255;0mHello, green!\x1b[m"):
    ...     code
    Foreground(color=Color(red=0, green=255, blue=0))
    'Hello, green!'
    <Attr.NORMAL: 0>
    """
    for piece in SGR_FORMAT.split(text):
        if piece:
            if not issgr(piece):
                yield piece
            else:
                yield from parse_sgr(piece)


def parse_sgr(text: Text) -> Iterable[Text | Attr | Foreground | Background]:
    r"""
    Parse a Select Graphic Rendition (SGR) escape sequence.

    This yields attributes in order they appear in the input. If an escape
    sequence is not supported, it is yielded separately as a string.

    A SGR escape sequence is a sequence that starts with an Control Sequence Introducer
    (CSI) and ends with an `m`.

    A CSI escape sequence is a sequence that starts with an escape character
    (`\033` or `\x1B`) followed by an opening bracket (`[` or `\x5B`).

    Examples
    --------
    >>> for code in parse_sgr(f"{CSI}1;31m"):
    ...     code
    <Attr.BOLD: 1>
    Color(red=179, green=16, blue=14)
    >>> for code in parse_sgr(f"{CSI}48;2;100;10;255m"):
    ...     code
    Background(color=Color(red=100, green=10, blue=255))
    >>> list(parse_sgr(f"{CSI}0m")) == list(parse_sgr("\x1B[m"))
    True
    """
    text = text[2:-1]
    if not text:
        yield Attr.NORMAL
    elif text.startswith("38"):
        text = text[3:]
        yield Foreground(parse_rgb(text))
    elif text.startswith("48"):
        text = text[3:]
        yield Background(parse_rgb(text))
    else:
        code: Text | int
        for code in text.split(";"):
            if code:
                code = int(code)
                try:
                    yield Attr(code)
                except ValueError:
                    try:
                        if 30 <= code <= 37:
                            yield Foreground(Color.from_int(code))
                        elif 40 <= code <= 47:
                            yield Background(Color.from_int(code))
                        else:
                            yield sgr(code)
                    except ValueError:
                        yield sgr(code)


def parse_rgb(text: Text) -> Color:
    r"""
    Parse only the relevant part of a 24-bit RGB color escape sequence (examples below).

    This raises an exception if the input does not start with "2;", as 256-color escape
    sequences are not supported at the moment.

    Examples
    --------
    >>> parse_rgb(f"2;255;100;0")
    Color(red=255, green=100, blue=0)
    """
    if not text.startswith("2;"):
        raise ValueError(f"{text} is not a 24-bit RGB color escape sequence")
    text = text[2:]
    return Color(*map(int, text.split(";")))


def issgr(text: Text) -> bool:
    r"""
    Check if a string is a Select Graphic Rendition (SGR) escape sequence.

    A SGR escape sequence is a sequence that starts with an Control Sequence Introducer
    (CSI) and ends with an `m`.

    A CSI escape sequence is a sequence that starts with an escape character
    (`\033` or `\x1B`) followed by an opening bracket (`[` or `\x5B`).

    Examples
    --------
    >>> issgr(f"{CSI}1;31m")
    True
    >>> issgr("\x1B[2J")
    False
    >>> issgr("\x1b]0;this is the window title\x1b\\")
    False
    >>> issgr("not an escape")
    False
    """
    return text.startswith(CSI) and text.endswith("m")


if __name__ == "__main__":
    for x in parse(f"{CSI}0;31mHello\x1b[m, \x1B[1;32mWorld!{CSI}0m"):
        print(repr(x))
