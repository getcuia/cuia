"""Facilities for working with colors."""

from dataclasses import dataclass
from typing import NamedTuple, Text

from kay.attr import sgr


class Color(NamedTuple):
    """
    An RGB color.

    Each color is represented by three integers in the range 0-255.
    """

    red: int
    green: int
    blue: int


BLACK = Color(0, 0, 0)
RED = Color(173, 0, 0)
GREEN = Color(0, 173, 0)
YELLOW = Color(173, 173, 0)
BLUE = Color(0, 0, 173)
MAGENTA = Color(173, 0, 173)
CYAN = Color(0, 173, 173)
WHITE = Color(173, 173, 173)


@dataclass(frozen=True)
class Foreground:
    """A foreground color."""

    color: Color

    def __str__(self) -> Text:
        """Return a string representation of this foreground color."""
        return sgr(f"38;2;{self.color.red};{self.color.green};{self.color.blue}")


@dataclass(frozen=True)
class Background:
    """A background color."""

    color: Color

    def __str__(self) -> Text:
        """Return a string representation of this background color."""
        return sgr(f"48;2;{self.color.red};{self.color.green};{self.color.blue}")
