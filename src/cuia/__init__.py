"""
> 🧓🏾🖥️ A delightful tiny framework for building reliable text-based applications.

cuia is a tiny Python library for building interactive terminal user interfaces
that is easy to use, fast and has a small memory footprint.

## How does it work

cuia is inspired by [Bubble Tea](https://github.com/charmbracelet/bubbletea)
(written in [Go](https://golang.org/)) and, on the surface, looks much like
it. In particular, cuia employs
[the Elm architecture](https://guide.elm-lang.org/architecture/) (TEA, named
after the [Elm programming language](https://elm-lang.org/)). What it means in
terms of output is that a cuia application creates a new screen representation of
the user interface (in fact, as a regular
[Python string](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str))
at each step. It might look as a serious memory overhead but, in fact, it will
never use more than 100kb to hold those string representations, even on
large screens[^how-big].

But, contrary to Bubble Tea, cuia is built on top of
[curses](https://docs.python.org/3/library/curses.html). curses is a standard
Python library (written in
[C](<https://en.wikipedia.org/wiki/C_(programming_language)>)) that wraps the
famous [ncurses](https://en.wikipedia.org/wiki/Ncurses) library (written in
C as well). ncurses does
[efficient screen updates](https://invisible-island.net/ncurses/hackguide.html#output)
and is thus quite fast. It works by comparing the contents of a screen buffer to
the contents of the actual screen and only updating where the contents have
changed. So, in general, cuia works in a similar way to
[virtual DOM](https://en.wikipedia.org/wiki/Virtual_DOM) tree updates (a
technique commonly used in
[JavaScript web frameworks](https://en.wikipedia.org/wiki/Comparison_of_JavaScript-based_web_frameworks)
such as [React](https://reactjs.org/)), except that it is a string buffer that
is updated, instead of a virtual DOM tree.

[^how-big]:
    My 22" desktop can't make a terminal larger than 211x55 characters. A single
    string representation would require a little over 10kb of storage in Python.
    It would then take **ten** string representations to be hold in memory at a
    single point in time for it to go beyond 100kb.
"""


__version__ = "0.1.0"


from .command import Command, quit
from .message import Key, Message, QuitMessage
from .program import Program
from .store import Store

__all__ = ["Command", "Key", "Message", "Program", "quit", "QuitMessage", "Store"]
