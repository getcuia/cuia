"""Facilities for working with attributes."""


from enum import Enum

ESC = "\033"
CSI = f"{ESC}["


class Attribute(Enum):
    r"""
    ANSI escape sequence attributes.

    Examples
    --------
    >>> Attribute.BOLD
    <Attribute.BOLD: 1>
    >>> str(Attribute.BOLD)
    '\x1b[1m'
    """

    NORMAL = 0
    BOLD = 1
    FAINT = 2
    # ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    #
    REVERSE = 7

    def __str__(self):
        """Return the ANSI escape sequence for this attribute."""
        return f"{CSI}{self.value}m"
