"""An object representing a color."""

from __future__ import annotations

from typing import NamedTuple

from ..misc import clamp
from .conversions import lch_to_luv, luv_to_lch, luv_to_xyz, xyz_to_luv


class Color(NamedTuple):
    """
    An RGB color.

    Each channel is represented by a float between zero and one.
    """

    red: float
    """Amount of red in the color."""
    green: float
    """Amount of green in the color."""
    blue: float
    """Amount of blue in the color."""

    @staticmethod
    def frombytes(red: int, green: int, blue: int) -> Color:
        """
        Create a color from bytes.

        The input values are expected to be between 0 and 255.

        Examples
        --------
        >>> Color.frombytes(0, 255, 255)
        Color(red=0.0, green=1.0, blue=1.0)
        """
        return Color(clamp(red / 255), clamp(green / 255), clamp(blue / 255))

    def tobytes(self) -> tuple[int, int, int]:
        """
        Return the bytes for this color.

        The output values are between 0 and 255.

        Examples
        --------
        >>> Color(red=0.0, green=1.0, blue=1.0).tobytes()
        (0, 255, 255)
        >>> Color.frombytes(10, 20, 30).tobytes() == (10, 20, 30)
        True
        """
        return (int(255 * self.red), int(255 * self.green), int(255 * self.blue))

    @staticmethod
    def fromxyz(x: float, y: float, z: float) -> Color:
        """
        Create a color from CIE XYZ coordinates.

        The input should refer to a D65/2° standard illuminant.

        **Source**:
        [From CIE XYZ to sRGB](https://en.wikipedia.org/wiki/SRGB#From_CIE_XYZ_to_sRGB).

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

        return Color(clamp(red), clamp(green), clamp(blue))

    def toxyz(self) -> tuple[float, float, float]:
        """
        Return the CIE XYZ color for this color.

        The output refers to a D65/2° standard illuminant.

        **Source**:
        [From sRGB to CIE XYZ](https://en.wikipedia.org/wiki/SRGB#From_sRGB_to_CIE_XYZ).

        Examples
        --------
        >>> Color(0, 0, 0).toxyz()
        (0.0, 0.0, 0.0)
        >>> Color(1, 1, 1).toxyz()
        (0.9505, 1.0, 1.089)
        >>> Color(0.5, 0.5, 0.5).toxyz()  # doctest: +NUMBER
        (0.203446, 0.214041, 0.233091)
        """
        red, green, blue = self.red, self.green, self.blue

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
        r"""
        Create a color from CIE L\*u\*v\* coordinates.

        The input refers to a D65/2° standard illuminant.

        Examples
        --------
        >>> Color.fromluv(0.533890, 0, 0)  # doctest: +NUMBER
        Color(red=0.5, green=0.5, blue=0.5)
        >>> Color.fromluv(0, 0, 0)
        Color(red=0.0, green=0.0, blue=0.0)
        """
        return Color.fromxyz(*luv_to_xyz(ell, u, v))

    def toluv(self) -> tuple[float, float, float]:
        r"""
        Return the CIE L\*u\*v\* color for this color.

        The output refers to a D65/2° standard illuminant.

        Examples
        --------
        >>> Color(0.5, 0.5, 0.5).toluv()  # doctest: +NUMBER
        (0.533890, 0.0, 0.0)
        """
        return xyz_to_luv(*self.toxyz())

    @staticmethod
    def fromlch(ell: float, c: float, h: float) -> Color:
        """
        Create a color from CIE LCh coordinates.

        The input refers to a D65/2° standard illuminant and the angle h (for hue) input
        is in radians.

        Examples
        --------
        >>> Color.fromlch(0.533890, 0, 0)  # doctest: +NUMBER
        Color(red=0.5, green=0.5, blue=0.5)
        """
        return Color.fromluv(*lch_to_luv(ell, c, h))

    def tolch(self) -> tuple[float, float, float]:
        """
        Return the CIE LCh color for this color.

        The output refers to a D65/2° standard illuminant and the angle h (for hue)
        output is in radians.

        Examples
        --------
        >>> Color(0.3, 0.6, 0.9).tolch()  # doctest: +NUMBER
        (0.616755, 0.786916, 4.317256)
        """
        return luv_to_lch(*self.toluv())

    @property
    def lightness(self) -> float:
        r"""
        Return the lightness of this color as per the CIE L\*u\*v\*/LCh color spaces.

        The lightness is a value between zero and one.

        Examples
        --------
        >>> Color(0, 0, 0).lightness
        0.0
        >>> Color.frombytes(23, 23, 23).lightness  # doctest: +NUMBER
        0.077396
        >>> c = Color.frombytes(0, 255, 0)
        >>> c.lightness  # doctest: +NUMBER
        0.877370
        """
        return self.toluv()[0]

    @property
    def chroma(self) -> float:
        """
        Return the chroma of this color as per the CIE LCh color space.

        The chroma is a value between zero and one.

        Examples
        --------
        >>> Color(0, 0, 0).chroma
        0.0
        >>> Color.frombytes(30, 60, 90).chroma  # doctest: +NUMBER
        0.2799813
        >>> Color.frombytes(255, 255, 255).chroma  # doctest: +NUMBER
        0.000171
        """
        return self.tolch()[1]

    @property
    def hue(self) -> float:
        """
        Return the hue of this color as per the CIE LCh color space.

        The hue is a value between 0 and 2π.

        Examples
        --------
        >>> Color(0, 0, 0).hue  # doctest: +NUMBER
        3.141593
        >>> Color.frombytes(30, 60, 90).hue  # doctest: +NUMBER
        4.296177
        >>> Color.frombytes(0, 255, 0).hue  # doctest: +NUMBER
        2.229197
        """
        return self.tolch()[2]

    def with_lightness(self, ell: float) -> Color:
        """
        Create a new color with the same chroma and hue but a new lightness.

        The lightness is a value between zero and one.

        Examples
        --------
        >>> Color.frombytes(0, 255, 0).with_lightness(0.5)  # doctest: +NUMBER
        Color(red=0.0, green=0.582453, blue=0.0)
        """
        _, u, v = self.toluv()
        return self.fromluv(ell, u, v)

    def with_chroma(self, c: float) -> Color:
        """
        Create a new color with the same hue and lightness but a new chroma.

        The chroma is a value between zero and one.

        Examples
        --------
        >>> Color.frombytes(0, 255, 0).with_chroma(0.5)  # doctest: +NUMBER
        Color(red=0.680477, green=0.922408, blue=0.680426)
        """
        ell, _, h = self.tolch()
        return self.fromlch(ell, c, h)

    def with_hue(self, h: float) -> Color:
        """
        Create a new color with the same chroma and lightness but a new hue.

        The hue is a value between 0 and 2π.

        Examples
        --------
        >>> Color.frombytes(0, 255, 0).with_hue(1.5)  # doctest: +NUMBER
        Color(red=0.900022, green=0.900897, blue=0.0)
        """
        ell, c, _ = self.tolch()
        return self.fromlch(ell, c, h)

    def islight(self) -> bool:
        """
        Return True if this color is light.

        A color is considered light if its lightness is greater than 0.5.

        Examples
        --------
        >>> from kay.color import BLACK, WHITE
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
        >>> from kay.color import BLACK, WHITE
        >>> BLACK.isdark()
        True
        >>> WHITE.isdark()
        False
        """
        return not self.islight()
