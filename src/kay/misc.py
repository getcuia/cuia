"""Random stuff that I don't know where to put."""

import re
from typing import Iterable, Pattern, Text


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """Clamp a value to a range."""
    return max(min_value, min(value, max_value))


def isplit(
    pattern: Pattern[Text], text: Text, include_separators: bool = False
) -> Iterable[Text]:
    r"""
    Split text into parts separated by the given pattern.

    This yields the text before the first match, then the match, then the text after
    the match and so on. If include_separators is False (the default), the separator is
    not included in the result. In any case, empty strings are never yielded.

    Examples
    --------
    >>> list(isplit(r'\s+', 'a b  c'))
    ['a', 'b', 'c']
    >>> list(isplit(r'\s+', 'a b  c', include_separators=True))
    ['a', ' ', 'b', '  ', 'c']
    """
    if isinstance(pattern, Text):
        pattern = re.compile(pattern)

    start, end = 0, 0
    for match in pattern.finditer(text):
        # Yield the text before the match.
        end = match.start()
        if piece := text[start:end]:
            yield piece

        # Yield the match.
        if include_separators and (piece := match.group(0)):
            yield piece

        # Update the start position.
        start = match.end()

    # Yield the text after the last match.
    if piece := text[start:]:
        yield piece
