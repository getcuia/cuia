"""Facilities for working with colors."""

from dataclasses import dataclass
from typing import NamedTuple, Text

from kay.attr import sgr


class Color(NamedTuple):
    """An RGB color."""

    red: int
    green: int
    blue: int


BLACK = Color(0, 0, 0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
YELLOW = Color(255, 255, 0)
BLUE = Color(0, 0, 255)
MAGENTA = Color(255, 0, 255)
CYAN = Color(0, 255, 255)
WHITE = Color(255, 255, 255)


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
