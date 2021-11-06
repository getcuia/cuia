"""
A simple ANSI escape sequence parser.

Only a subset of the ANSI escape sequences are supported, namely a subset of
the SGR (Select Graphic Rendition) escape sequences.
"""

from __future__ import annotations

import re
from typing import Iterable, Text

SGR_FORMAT = re.compile(r"(\x1B\[[0-9;]*m)")


def parse(text: Text) -> Iterable[Text | int]:
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
    >>> for code in parse("\033[0;31mHello\x1b[m, \x1B[1;32mWorld!\033[0m"):
    ...     code
    0
    31
    'Hello'
    0
    ', '
    1
    32
    'World!'
    0
    """
    for piece in SGR_FORMAT.split(text):
        if piece:
            if not issgr(piece):
                yield piece
            else:
                yield from parse_sgr(piece)


def parse_sgr(text: Text) -> Iterable[int]:
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
    >>> for code in parse_sgr("\033[1;31m"):
    ...     code
    1
    31
    >>> list(parse_sgr("\033[0m")) == list(parse_sgr("\x1B[m"))
    True
    """
    text = text[2:-1]
    if not text:
        yield 0
    else:
        for code in text.split(";"):
            if code:
                yield int(code)


def issgr(text: Text) -> bool:
    r"""
    Check if a string is a Select Graphic Rendition (SGR) escape sequence.

    A SGR escape sequence is a sequence that starts with an Control Sequence Introducer
    (CSI) and ends with an `m`.

    A CSI escape sequence is a sequence that starts with an escape character
    (`\033` or `\x1B`) followed by an opening bracket (`[` or `\x5B`).

    Examples
    --------
    >>> issgr("\033[1;31m")
    True
    >>> issgr("\x1B[2J")
    False
    >>> issgr("\x1b]0;this is the window title\x1b\\")
    False
    >>> issgr("not an escape")
    False
    """
    return text.startswith("\x1B[") and text.endswith("m")


if __name__ == "__main__":
    text = "\033[0;31mHello\x1b[m, \x1B[1;32mWorld!\033[0m"
    pieces = list(parse(text))
    print(len(pieces))
    for piece in pieces:
        # print(type(piece))
        print(repr(piece))
        # print(piece)
