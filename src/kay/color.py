"""Facilities for working with colors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Text

from kay.attr import sgr


class Color(NamedTuple):
    """
    An RGB color.

    Each color is represented by three floats between 0.0 and 1.0.
    """

    red: float
    green: float
    blue: float

    @staticmethod
    def frombytes(red: int, green: int, blue: int) -> Color:
        """
        Create a Color from bytes.

        Examples
        --------
        >>> Color.frombytes(0, 0, 0)
        Color(red=0.0, green=0.0, blue=0.0)
        >>> Color.frombytes(255, 255, 255)
        Color(red=1.0, green=1.0, blue=1.0)
        """
        return Color(red / 255, green / 255, blue / 255)

    @staticmethod
    def fromint(code: int) -> Color:
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

    def brightness(self) -> float:
        """
        Return the brightness of this color.

        The brightness is a value between 0.0 and 1.0.

        Source: [Web Content Accessibility Guidelines (Version 1.0)](https://www.w3.org/TR/AERT/#color-contrast).

        Examples
        --------
        >>> Color(0, 0, 0).brightness()
        0.0
        >>> Color.frombytes(255, 255, 255).brightness()  # doctest: +NUMBER
        1.0
        """
        return 0.299 * self.red + 0.587 * self.green + 0.114 * self.blue

    def is_light(self) -> bool:
        """
        Return True if this color is light.

        A color is considered light if its brightness is greater than 0.5.

        Examples
        --------
        >>> BLACK.is_light()
        False
        >>> WHITE.is_light()
        True
        """
        return self.brightness() > 0.5

    def is_dark(self) -> bool:
        """
        Return True if this color is dark.

        A color is considered dark if it is not light.

        Examples
        --------
        >>> BLACK.is_dark()
        True
        >>> WHITE.is_dark()
        False
        """
        return not self.is_light()

    def luminance(self) -> float:
        """
        Return the luminance of this color.

        The luminance is a value between 0.0 and 1.0.

        Source: [Web Content Accessibility Guidelines (Version 2.0)](http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef).

        Examples
        --------
        >>> Color(0, 0, 0).luminance()
        0.0
        >>> Color.frombytes(23, 23, 23).luminance()  # doctest: +NUMBER
        0.0085681256
        >>> Color.frombytes(255, 255, 255).luminance()
        1.0
        """
        r = (
            self.red / 12.92
            if self.red <= 0.03928
            else ((self.red + 0.055) / 1.055) ** 2.4
        )
        g = (
            self.green / 12.92
            if self.green <= 0.03928
            else ((self.green + 0.055) / 1.055) ** 2.4
        )
        b = (
            self.blue / 12.92
            if self.blue <= 0.03928
            else ((self.blue + 0.055) / 1.055) ** 2.4
        )
        return 0.2126 * r + 0.7152 * g + 0.0722 * b


# The following colors were taken as the average of the colors found in
# <https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit>.
BLACK = Color.frombytes(1, 1, 1)  # Color.frombytes(0, 0, 0)
RED = Color.frombytes(179, 16, 14)  # Color.frombytes(173, 0, 0)
GREEN = Color.frombytes(11, 172, 22)  # Color.frombytes(0, 173, 0)
YELLOW = Color.frombytes(203, 176, 27)  # Color.frombytes(173, 173, 0)
BLUE = Color.frombytes(10, 30, 186)  # Color.frombytes(0, 0, 173)
MAGENTA = Color.frombytes(155, 20, 164)  # Color.frombytes(173, 0, 173)
CYAN = Color.frombytes(34, 150, 184)  # Color.frombytes(0, 173, 173)
WHITE = Color.frombytes(204, 205, 205)  # Color.frombytes(173, 173, 173)


@dataclass(frozen=True)
class Foreground:
    """A foreground color."""

    color: Color

    def __str__(self) -> Text:
        """Return a string representation of this foreground color."""
        if self.color == BLACK:
            return sgr("30")
        if self.color == RED:
            return sgr("31")
        if self.color == GREEN:
            return sgr("32")
        if self.color == YELLOW:
            return sgr("33")
        if self.color == BLUE:
            return sgr("34")
        if self.color == MAGENTA:
            return sgr("35")
        if self.color == CYAN:
            return sgr("36")
        if self.color == WHITE:
            return sgr("37")
        return sgr(f"38;2;{self.color.red};{self.color.green};{self.color.blue}")


@dataclass(frozen=True)
class Background:
    """A background color."""

    color: Color

    def __str__(self) -> Text:
        """Return a string representation of this background color."""
        if self.color == BLACK:
            return sgr("40")
        if self.color == RED:
            return sgr("41")
        if self.color == GREEN:
            return sgr("42")
        if self.color == YELLOW:
            return sgr("43")
        if self.color == BLUE:
            return sgr("44")
        if self.color == MAGENTA:
            return sgr("45")
        if self.color == CYAN:
            return sgr("46")
        if self.color == WHITE:
            return sgr("47")
        return sgr(f"48;2;{self.color.red};{self.color.green};{self.color.blue}")
