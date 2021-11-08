"""Facilities for working with colors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, NamedTuple, Text

from kay.ansi.token import Token


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

    def tobytes(self) -> tuple[int, int, int]:
        """
        Return the bytes for this color.

        Examples
        --------
        >>> Color.frombytes(10, 20, 30).tobytes() == (10, 20, 30)
        True
        """
        return (int(255 * self.red), int(255 * self.green), int(255 * self.blue))

    @staticmethod
    def fromxyz(x: float, y: float, z: float) -> Color:
        """
        Create a Color from XYZ coordinates.

        The input refers to a D65/2° standard illuminant.

        Source: https://en.wikipedia.org/wiki/SRGB#The_forward_transformation_(CIE_XYZ_to_sRGB).

        Examples
        --------
        >>> Color.fromxyz(0, 0, 0)
        Color(red=0.0, green=0.0, blue=0.0)
        >>> Color.fromxyz(0.9505, 1.0000, 1.0890)  # doctest: +NUMBER
        Color(red=1.0, green=1.0, blue=1.0)
        >>> Color.fromxyz(0.203446104, 0.214041140, 0.233090801)  # doctest: +NUMBER
        Color(red=0.5, green=0.5, blue=0.5)
        """
        # We're using a higher precision matrix here see
        # <https://en.wikipedia.org/wiki/SRGB#sYCC_extended-gamut_transformation>
        red = 3.2406254 * x - 1.537208 * y - 0.4986286 * z
        green = -0.9689307 * x + 1.8757561 * y + 0.0415175 * z
        blue = 0.0557101 * x - 0.2040211 * y + 1.0569959 * z

        if red > 0.0031308:
            red = 1.055 * (red ** (1 / 2.4)) - 0.055
        else:
            red = 12.92 * red
        if green > 0.0031308:
            green = 1.055 * (green ** (1 / 2.4)) - 0.055
        else:
            green = 12.92 * green
        if blue > 0.0031308:
            blue = 1.055 * (blue ** (1 / 2.4)) - 0.055
        else:
            blue = 12.92 * blue

        return Color(red, green, blue)

    def toxyz(self) -> tuple[float, float, float]:
        """
        Return the XYZ color for this color.

        The output refers to a D65/2° standard illuminant.

        Source: https://en.wikipedia.org/wiki/SRGB#The_reverse_transformation_(sRGB_to_CIE_XYZ).

        Examples
        --------
        >>> Color(0, 0, 0).toxyz()
        (0.0, 0.0, 0.0)
        >>> Color(1, 1, 1).toxyz()  # doctest: +NUMBER
        (0.9505, 1.0000, 1.0890)
        >>> Color(0.5, 0.5, 0.5).toxyz()  # doctest: +NUMBER
        (0.203446104, 0.214041140, 0.233090801)
        """
        red, green, blue = self

        if red > 0.04045:
            red = ((red + 0.055) / 1.055) ** 2.4
        else:
            red = red / 12.92
        if green > 0.04045:
            green = ((green + 0.055) / 1.055) ** 2.4
        else:
            green = green / 12.92
        if blue > 0.04045:
            blue = ((blue + 0.055) / 1.055) ** 2.4
        else:
            blue = blue / 12.92

        x = 0.4124 * red + 0.3576 * green + 0.1805 * blue
        y = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        z = 0.0193 * red + 0.1192 * green + 0.9505 * blue
        return x, y, z

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

    def _tokens(self) -> Iterator[Token]:
        """
        Yield **dummy** ANSI tokens for this color.

        The tokens yielded are not actually valid ANSI tokens because the
        first token always starts at zero (when it should have been between
        30-38, 40-48, etc.)

        This is for internal use only.

        Examples
        --------
        >>> list(BLACK._tokens())
        [Token(marker='m', param=0)]
        >>> list(WHITE._tokens())
        [Token(marker='m', param=7)]
        """
        if self == BLACK:
            yield Token(marker="m", param=0)
        elif self == RED:
            yield Token(marker="m", param=1)
        elif self == GREEN:
            yield Token(marker="m", param=2)
        elif self == YELLOW:
            yield Token(marker="m", param=3)
        elif self == BLUE:
            yield Token(marker="m", param=4)
        elif self == MAGENTA:
            yield Token(marker="m", param=5)
        elif self == CYAN:
            yield Token(marker="m", param=6)
        elif self == WHITE:
            yield Token(marker="m", param=7)
        else:
            yield Token(marker="m", param=8)
            yield Token(marker="m", param=2)

            red, green, blue = self.tobytes()
            yield Token(marker="m", param=red)
            yield Token(marker="m", param=green)
            yield Token(marker="m", param=blue)

    def brightness(self) -> float:
        """
        Return the brightness of this color.

        The brightness is a value between 0.0 and 1.0.

        Source: [Web Content Accessibility Guidelines (Version 1.0)](https://www.w3.org/TR/AERT/#color-contrast).

        Examples
        --------
        >>> Color(0, 0, 0).brightness()
        0.0
        >>> Color.frombytes(23, 23, 23).brightness()  # doctest: +NUMBER
        0.0902
        >>> Color.frombytes(255, 255, 255).brightness()  # doctest: +NUMBER
        1.0
        """
        return 0.299 * self.red + 0.587 * self.green + 0.114 * self.blue

    def islight(self) -> bool:
        """
        Return True if this color is light.

        A color is considered light if its brightness is greater than 0.5.

        Examples
        --------
        >>> BLACK.islight()
        False
        >>> WHITE.islight()
        True
        """
        return self.brightness() > 0.5

    def isdark(self) -> bool:
        """
        Return True if this color is dark.

        A color is considered dark if it is not light.

        Examples
        --------
        >>> BLACK.isdark()
        True
        >>> WHITE.isdark()
        False
        """
        return not self.islight()

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

    def tokens(self) -> Iterable[Token]:
        """Yield the tokens to set the foreground color."""
        _tokens = self.color._tokens()
        head = next(_tokens)
        yield Token(marker=head.marker, param=head.param + 30)
        yield from _tokens

    def __str__(self) -> Text:
        """Return a string representation of this foreground color."""
        return Text(*self.tokens())


@dataclass(frozen=True)
class Background:
    """A background color."""

    color: Color

    def tokens(self) -> Iterable[Token]:
        """Yield the tokens to set the background color."""
        _tokens = self.color._tokens()
        head = next(_tokens)
        yield Token(marker=head.marker, param=head.param + 40)
        yield from _tokens

    def __str__(self) -> Text:
        """Return a string representation of this background color."""
        return Text(*self.tokens())
