"""Facilities for working with ANSI escape sequences."""


from __future__ import annotations

import re
from typing import Iterable, Text

from kay.ansi.token import Token

PATTERN = re.compile(r"(\N{ESC}\[[\d;]*[a-zA-Z])")


def escape(tokens: Token | Iterable[Token]) -> Text:
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
    # TODO: encode automatically if not tokens using a map

    def _escape(kind: Text, data: int | Text) -> Text:
        return f"\N{ESC}[{data or ''}{kind}"

    if isinstance(tokens, Token):
        return _escape(tokens.kind, tokens.data)

    # TODO: make a fold/reduce
    first, *rest = tokens
    res = _escape(first.kind, first.data)[:-1]
    kind = first.kind
    for token in rest:
        if token.kind == kind:
            res += f";{token.data or ''}"
        else:
            res += f"{kind}{_escape(token.kind, token.data)[:-1]}"
            kind = token.kind
    return f"{res}{kind}"
