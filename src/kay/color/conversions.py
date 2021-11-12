"""Color conversions."""


from __future__ import annotations

import math


def xyz_to_uv(x: float, y: float, z: float) -> tuple[float, float]:
    """Convert CIE XYZ to chromaticity coordinates u'v'."""
    if x == y == 0:
        return 0, 0
    d = x + 15 * y + 3 * z
    return 4 * x / d, 9 * y / d


def luv_to_uv(ell: float, u: float, v: float) -> tuple[float, float]:
    r"""Convert CIE L\*u\*v\* to chromaticity coordinates u'v'."""
    d = 13 * ell
    return u / d + REF_UV_D65_2[0], v / d + REF_UV_D65_2[1]


def xyz_to_luv(x: float, y: float, z: float) -> tuple[float, float, float]:
    r"""
    Convert CIE XYZ to CIE L\*u\*v\*.

    The input refers to a D65/2° standard illuminant.

    **Source**:
    [The forward transformation](https://en.wikipedia.org/wiki/CIELUV#The_forward_transformation).

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
    r"""
    Convert CIE L\*u\*v\* to CIE XYZ.

    The output refers to a D65/2° standard illuminant.

    **Source**:
    [The reverse transformation](https://en.wikipedia.org/wiki/CIELUV#The_reverse_transformation).

    Examples
    --------
    >>> luv_to_xyz(0.5, 0.5, 0.5)  # doctest: +NUMBER
    (0.208831, 0.184187, 0.022845)
    """
    if ell == 0:
        return 0, 0, 0

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
    r"""
    Convert CIE L\*u\*v\* to CIE LCh.

    The input refers to a D65/2° standard illuminant and the angle h (for hue) output is
    in radians.

    **Source**:
    [Cylindrical representation (CIELCh)](https://en.wikipedia.org/wiki/CIELUV#Cylindrical_representation_(CIELCh)).

    Examples
    --------
    >>> luv_to_lch(0.5, 0.5, 0.5)  # doctest: +NUMBER
    (0.5, 0.707107, 0.7853982)
    >>> luv_to_lch(0.616729, -0.302960, -0.726142)  # doctest: +NUMBER
    (0.616729, 0.786808, 4.317128)
    """
    h = math.atan2(v, u)
    c = math.hypot(v, u)
    h = h + math.tau if h < 0 else h
    return ell, c, h


def lch_to_luv(ell: float, c: float, h: float) -> tuple[float, float, float]:
    r"""
    Convert CIE LCh to CIE L\*u\*v\*.

    The output refers to a D65/2° standard illuminant and the angle h (for hue) input is
    in radians.

    **Source**: [Polar CIELUV](https://observablehq.com/@mbostock/luv-and-hcl#cell-219).

    Examples
    --------
    >>> lch_to_luv(0.5, 0.707107, 0.7853981633974483)  # doctest: +NUMBER
    (0.5, 0.5, 0.5)
    """
    u = c * math.cos(h)
    v = c * math.sin(h)
    return ell, u, v


# CIE XYZ reference values to a D65/2° standard illuminant.
REF_XYZ_D65_2 = 0.95047, 1.00000, 1.08883
REF_UV_D65_2 = xyz_to_uv(*REF_XYZ_D65_2)


# Constant used in the CIE L*u*v* to CIE XYZ conversion.
KAPPA = 903.2962962962961
