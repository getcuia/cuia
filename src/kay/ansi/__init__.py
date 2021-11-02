"""
ANSI Escape Sequences.

Some simple utilities for working with ANSI escape sequences.
Good resources about ANSI escape sequences:
- [fnky/ANSI.md][fnky-ansi-md].

[fnky-ansi-md]: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""


from __future__ import annotations


# Sequences
ESC = "\x1B"  # ANSI escape character
CSI = "\x9B"  # or `f"{ESC}["`, Control Sequence Introducer
DCS = "\x90"  # or `f"{ESC}P"`, Device Control String
OSC = "\x9D"  # or `f"{ESC}]"`, Operating System Command


# General ASCII Codes
BEL = "\x07"  # Terminal bell
BS = "\x08"  # Backspace
HT = "\x09"  # Horizontal tab
LF = NL = "\x0A"  # Line feed (new line)
VT = "\x0B"  # Vertical tab
FF = NP = "\x0C"  # Form feed (new page)
CR = "\x0D"  # Carriage return
# ESC = "\x1B"  # ANSI escape character
DEL = "\x7F"  # Delete


def csi(code: str | int):
    """
    Return an ANSI escape sequence for the given code.

    Idea taken from [here](https://realpython.com/lessons/ansi-escape-sequences/).
    """
    return f"{CSI}{code}m"


if __name__ == "__main__":
    print("this is ", csi(31), "really", csi(0), " important", sep="")
    print("this is ", csi("31;1"), "really", csi(0), " important", sep="")
    print("this is ", csi("31;1;4"), "really", csi(0), " important", sep="")
    print("this is a bell ", csi(BEL), sep="")
