"""Facilities for working with colors."""


from ._color import Color

# The following colors were taken as the average of the colors found in
# <https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit>.
# They had then their lightness adjusted to be closer to the average of the
# colors in the table.
LIGHTNESS = 0.8  # TODO: the not bright colors can have half the lightness
BLACK_LIGHTNESS = min(LIGHTNESS ** 10, 1 - LIGHTNESS ** 10)
BLACK = Color.frombytes(1, 1, 1).with_lightness(
    BLACK_LIGHTNESS
)  # Color.frombytes(0, 0, 0)
RED = Color.frombytes(179, 16, 14).with_lightness(
    LIGHTNESS
)  # Color.frombytes(173, 0, 0)
GREEN = Color.frombytes(11, 172, 22).with_lightness(
    LIGHTNESS
)  # Color.frombytes(0, 173, 0)
YELLOW = Color.frombytes(203, 176, 27).with_lightness(
    LIGHTNESS
)  # Color.frombytes(173, 173, 0)
BLUE = Color.frombytes(10, 30, 186).with_lightness(
    LIGHTNESS
)  # Color.frombytes(0, 0, 173)
MAGENTA = Color.frombytes(155, 20, 164).with_lightness(
    LIGHTNESS
)  # Color.frombytes(173, 0, 173)
CYAN = Color.frombytes(34, 150, 184).with_lightness(
    LIGHTNESS
)  # Color.frombytes(0, 173, 173)
WHITE = Color.frombytes(204, 205, 205).with_lightness(
    1 - BLACK_LIGHTNESS
)  # Color.frombytes(173, 173, 173)

assert BLACK.lightness < WHITE.lightness
