"""Simple utilities for working with ANSI escape sequences."""




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
