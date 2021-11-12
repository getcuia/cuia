"""Foreground and background colors."""


from dataclasses import dataclass
from typing import Text

from kay import ansi, color


@dataclass(frozen=True)
class Ground:
    """A ground color."""

    color: color.Color

    def __str__(self) -> Text:
        """Return the color as a string."""
        return ansi.escape(ansi.token.encode(self))


@dataclass(frozen=True)
class Fore(Ground):
    """
    A terminal foreground color.

    Examples
    --------
    >>> Fore(color.RED)
    Fore(color=Color(red=1.0, green=0.5826106699754192, blue=0.5805635742506021))
    """


@dataclass(frozen=True)
class Back(Ground):
    """
    A terminal background color.

    Examples
    --------
    >>> Back(color.RED)
    Back(color=Color(red=1.0, green=0.5826106699754192, blue=0.5805635742506021))
    """
