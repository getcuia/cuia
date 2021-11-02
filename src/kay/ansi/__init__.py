"""
Simple utilities for working with ANSI escape sequences.

Good resources about ANSI escape sequences:
- [fnky/ANSI.md][fnky-ansi-md].

[fnky-ansi-md]: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""


from __future__ import annotations


def esc(code: str | int):
    """
    Return an ANSI escape sequence for the given code.

    Idea taken from [here](https://realpython.com/lessons/ansi-escape-sequences/).
    """
    return f"\033[{code}m"


if __name__ == "__main__":
    print("this is ", esc("31"), "really", esc(0), " important", sep="")
    print("this is ", esc("31;1"), "really", esc(0), " important", sep="")
    print("this is ", esc("31;1;4"), "really", esc(0), " important", sep="")
