"""Facilities for working with colors."""

from __future__ import annotations

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

    @staticmethod
    def from_int(code: int) -> Color:
        """
        Create a color from an integer.

        The integer should be a 3-bit SGR color code.
        A ValueError is raised otherwise.
        """
        if code in {30, 40}:
            return BLACK
        if code in {31, 41}:
            return RED
        if code in {32, 42}:
            return GREEN
        if code in {33, 43}:
            return YELLOW
        if code in {34, 44}:
            return BLUE
        if code in {35, 45}:
            return MAGENTA
        if code in {36, 46}:
            return CYAN
        if code in {37, 47}:
            return WHITE
        raise ValueError(f"Invalid color code: {code}")


# The following colors were taken as the average of the colors found in
# <https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit>.
BLACK = Color(1, 1, 1)  # Color(0, 0, 0)
RED = Color(179, 16, 14)  # Color(173, 0, 0)
GREEN = Color(11, 172, 22)  # Color(0, 173, 0)
YELLOW = Color(203, 176, 27)  # Color(173, 173, 0)
BLUE = Color(10, 30, 186)  # Color(0, 0, 173)
MAGENTA = Color(155, 20, 164)  # Color(173, 0, 173)
CYAN = Color(34, 150, 184)  # Color(0, 173, 173)
WHITE = Color(204, 205, 205)  # Color(173, 173, 173)


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
