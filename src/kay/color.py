"""Facilities for working with colors."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Iterator, NamedTuple, Text

from kay.ansi.token import Token


def xyz_to_uv(x: float, y: float, z: float) -> tuple[float, float]:
    """Convert XYZ to chromaticity coordinates u'v'."""
    if x == y == 0:
        return 0, 0
    d = x + 15 * y + 3 * z
    return 4 * x / d, 9 * y / d


def luv_to_uv(ell: float, u: float, v: float) -> tuple[float, float]:
    """Convert CIE L*u*v* to chromaticity coordinates u'v'."""
    d = 13 * ell
    return u / d + REF_UV_D65_2[0], v / d + REF_UV_D65_2[1]


# CIE XYZ reference values to a D65/2° standard illuminant.
REF_XYZ_D65_2 = 0.95047, 1.00000, 1.08883
REF_UV_D65_2 = xyz_to_uv(*REF_XYZ_D65_2)


# Constant used in the CIE L*u*v* to XYZ conversion.
KAPPA = 903.2962962962961


class Color(NamedTuple):
    """
    An RGB color.

    Each color is represented by three floats between 0 and 1.
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
        >>> Color.fromxyz(0.9505, 1, 1.0890)  # doctest: +NUMBER
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
    def fromluv(ell: float, u: float, v: float) -> Color:
        """
        Create a Color from CIE L*u*v* coordinates.

        The input refers to a D65/2° standard illuminant.

        Source: https://en.wikipedia.org/wiki/CIELUV#The_reverse_transformation.

        Examples
        --------
        >>> Color.fromluv(0.533890, 0, 0)  # doctest: +NUMBER
        Color(red=0.5, green=0.5, blue=0.5)
        """
        return Color.fromxyz(*luv_to_xyz(ell, u, v))

    def toluv(self) -> tuple[float, float, float]:
        """
        Return the CIE L*u*v* color for this color.

        The output refers to a D65/2° standard illuminant.

        Source: https://en.wikipedia.org/wiki/CIELUV#The_reverse_transformation.

        Examples
        --------
        >>> Color(0.5, 0.5, 0.5).toluv()  # doctest: +NUMBER
        (0.533890, 0.0, 0.0)
        """
        return xyz_to_luv(*self.toxyz())

    @staticmethod
    def fromlch(ell: float, c: float, h: float) -> Color:
        """
        Create a Color from CIE LCh coordinates.

        The input refers to a D65/2° standard illuminant.
        The returned angle h is in radians.

        Examples
        --------
        >>> Color.fromlch(0.533890, 0, 0)  # doctest: +NUMBER
        Color(red=0.5, green=0.5, blue=0.5)
        """
        return Color.fromluv(*lch_to_luv(ell, c, h))

    def tolch(self) -> tuple[float, float, float]:
        """
        Return the CIE LCh color for this color.

        The output refers to a D65/2° standard illuminant.
        The returned angle h is in radians.

        Examples
        --------
        >>> Color(0.3, 0.6, 0.9).tolch()  # doctest: +NUMBER
        (0.617, 0.787, 4.317)
        """
        return luv_to_lch(*self.toluv())

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

    @property
    def lightness(self) -> float:
        """
        Return the lightness of this color as per the CIE L*u*v*/LCh color spaces.

        The lightness is a value between 0 and 1.

        Examples
        --------
        >>> Color(0, 0, 0).lightness
        0.0
        >>> Color.frombytes(23, 23, 23).lightness  # doctest: +NUMBER
        0.077396
        >>> Color.frombytes(255, 255, 255).lightness  # doctest: +NUMBER
        1.0
        """
        return self.toluv()[0]

    @property
    def chroma(self) -> float:
        """
        Return the chroma of this color as per the CIE LCh color space.

        The chroma is a value between 0 and 1.

        Examples
        --------
        >>> Color(0, 0, 0).chroma
        0.0
        >>> Color.frombytes(30, 60, 90).chroma  # doctest: +NUMBER
        0.3
        >>> Color.frombytes(255, 255, 255).chroma  # doctest: +NUMBER
        0.0
        """
        return self.tolch()[1]

    @property
    def hue(self) -> float:
        """
        Return the hue of this color as per the CIE LCh color space.

        The hue is a value between 0 and 2π.

        Examples
        --------
        >>> Color(0, 0, 0).hue
        3.141592653589793
        >>> Color.frombytes(30, 60, 90).hue  # doctest: +NUMBER
        4.2
        >>> Color.frombytes(0, 255, 0).hue  # doctest: +NUMBER
        2.3
        """
        return self.tolch()[2]

    def islight(self) -> bool:
        """
        Return True if this color is light.

        A color is considered light if its lightness is greater than 0.5.

        Examples
        --------
        >>> BLACK.islight()
        False
        >>> WHITE.islight()
        True
        """
        return self.lightness > 0.5

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


def xyz_to_luv(x: float, y: float, z: float) -> tuple[float, float, float]:
    """
    Convert CIE XYZ to CIE L*u*v*.

    The input refers to a D65/2° standard illuminant.

    Source: https://en.wikipedia.org/wiki/CIELUV#The_forward_transformation.

    Examples
    --------
    >>> xyz_to_luv(*REF_XYZ_D65_2)
    (1.0, 0.0, 0.0)
    >>> xyz_to_luv(0.5, 0.5, 0.5)  # doctest: +NUMBER
    (0.760693, 0.125457, 0.052885)
    """
    u, v = xyz_to_uv(x, y, z)

    epsilon = 0.008856451679035631
    if y > epsilon:
        ell = 116 * y ** (1 / 3) - 16
    else:
        ell = KAPPA * y
    u, v = 13 * ell * (u - REF_UV_D65_2[0]), 13 * ell * (v - REF_UV_D65_2[1])

    return ell / 100, u / 100, v / 100


def luv_to_xyz(ell: float, u: float, v: float) -> tuple[float, float, float]:
    """
    Convert CIE L*u*v* to CIE XYZ.

    The output refers to a D65/2° standard illuminant.

    Source: https://en.wikipedia.org/wiki/CIELUV#The_reverse_transformation.

    Examples
    --------
    >>> luv_to_xyz(0.5, 0.5, 0.5)  # doctest: +NUMBER
    (0.208831, 0.184187, 0.022845)
    """
    ell, u, v = 100 * ell, 100 * u, 100 * v
    u, v = luv_to_uv(ell, u, v)

    four_v = 4 * v
    if ell > 8:
        y = ((ell + 16) / 116) ** 3
    else:
        y = ell / KAPPA
    x, z = 9 * y * u / four_v, y * (12 - 3 * u - 20 * v) / four_v

    return x, y, z


def luv_to_lch(ell: float, u: float, v: float) -> tuple[float, float, float]:
    """
    Convert CIE L*u*v* to CIE LCh.

    The input refers to a D65/2° standard illuminant.
    The returned angle h is in radians.

    Source: https://en.wikipedia.org/wiki/CIELUV#Cylindrical_representation_(CIELCh).

    Examples
    --------
    >>> luv_to_lch(0.5, 0.5, 0.5)  # doctest: +NUMBER
    (0.5, 0.707107, 0.7853981633974483)
    >>> luv_to_lch(0.616729, -0.302960, -0.726142)  # doctest: +NUMBER
    (0.616729, 0.786808, 4.317128)
    """
    h = math.atan2(v, u)
    c = math.hypot(v, u)
    h = h + math.tau if h < 0 else h
    return ell, c, h


def lch_to_luv(ell: float, c: float, h: float) -> tuple[float, float, float]:
    """
    Convert CIE LCh to CIE L*u*v*.

    The output refers to a D65/2° standard illuminant.
    The input angle h is in radians.

    Source: https://observablehq.com/@mbostock/luv-and-hcl#cell-219.

    Examples
    --------
    >>> lch_to_luv(0.5, 0.707107, 0.7853981633974483)  # doctest: +NUMBER
    (0.5, 0.5, 0.5)
    """
    u = c * math.cos(h)
    v = c * math.sin(h)
    return ell, u, v
