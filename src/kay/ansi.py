"""
A simple ANSI escape sequence parser.

Only a subset of the ANSI escape sequences are supported, namely a subset of
the SGR (Select Graphic Rendition) escape sequences.
"""

from __future__ import annotations

import re
from typing import Iterable, Text

from kay.attr import CSI, Attr, sgr

SGR_FORMAT = re.compile(rf"({CSI}[0-9;]*m)")


def parse(text: Text) -> Iterable[Text | Attr]:
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
    '\x1b[31m'
    'Hello'
    <Attr.NORMAL: 0>
    ', '
    <Attr.BOLD: 1>
    '\x1b[32m'
    'World!'
    <Attr.NORMAL: 0>
    """
    for piece in SGR_FORMAT.split(text):
        if piece:
            if not issgr(piece):
                yield piece
            else:
                yield from parse_sgr(piece)


def parse_sgr(text: Text) -> Iterable[Text | Attr]:
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
    '\x1b[31m'
    >>> list(parse_sgr(f"{CSI}0m")) == list(parse_sgr("\x1B[m"))
    True
    """
    text = text[2:-1]
    if not text:
        yield Attr.NORMAL
    else:
        code: Text | int
        for code in text.split(";"):
            if code:
                code = int(code)
                try:
                    yield Attr(code)
                except ValueError:
                    yield sgr(code)


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
    return text.startswith(f"{CSI}") and text.endswith("m")


if __name__ == "__main__":
    for x in parse(f"{CSI}0;31mHello\x1b[m, \x1B[1;32mWorld!{CSI}0m"):
        print(repr(x))
