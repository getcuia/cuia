# kay 🧓🏾🖥️

> A delightful tiny framework for building reliable text-based applications.

kay is a tiny Python library for building interactive terminal user interfaces
that is easy to use, fast and has a very small memory footprint.

## How does it work

kay is inspired by [bubbletea](https://github.com/charmbracelet/bubbletea)
(written in [Go](https://golang.org/)) and, on the surface, looks very much like
it. In particular, kay employs
[the Elm architecture](https://guide.elm-lang.org/architecture/) (TEA, named
after the [Elm programming language](https://elm-lang.org/)). What it means in
terms of output is that a kay application creates a new screen representation of
the user interface (in fact, as a regular
[Python string](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str))
at each step. It might look as a serious memory overhead but, in fact, it will
never use more than 100kb to hold those string representations, even on very
large screens[^how-big].

But, contrary to bubbletea, kay is built on top of
[curses](https://docs.python.org/3/library/curses.html). curses is a standard
Python library (written in
[C](<https://en.wikipedia.org/wiki/C_(programming_language)>)) that wraps the
very famous [ncurses](https://en.wikipedia.org/wiki/Ncurses) library (written in
C as well). ncurses does
[very efficient screen updates](https://invisible-island.net/ncurses/hackguide.html#output)
and is thus very fast. It works by comparing the contents of a screen buffer to
the contents of the actual screen and only updating where the contents have
changed. So, in general, kay works in a similar way to
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

### Attributes and color

Since curses handles colors and attributes for us in a terminal-independent way,
directly using ANSI escape sequences is not possible. But since kay uses a
simple string output, colors and attributes are supported by a simple ANSI
escape sequence parser. A subset of ECMA-48 (the standard for ANSI escape
sequences) is supported:

**Attributes**:

-   `BOLD` (Extra bright/bold): `\x1b[1m` (ECMA-48, VT100, xterm, linux)
-   `FAINT` (Half bright/dim): `\x1b[2m` (ECMA-48, xterm, linux)
-   `UNDERLINE` (Underlined): `\x1b[4m` (ECMA-48, VT100, xterm, linux)
-   `BLINK` (Blinking): `\x1b[5m` (ECMA-48, VT100, xterm, linux)
-   `REVERSE` (Reverse video): `\x1b[7m` (ECMA-48, VT100, xterm, linux)

_Note 0:_ references available:

-   [ECMA-48](https://www.ecma-international.org/publications-and-standards/standards/ecma-48/)
-   [VT100](https://vt100.net/docs/vt100-ug/chapter3.html#SGR)
-   [xterm](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html)
-   [linux](https://man7.org/linux/man-pages/man4/console_codes.4.html) (the
    linux console, that is)

_Note 1:_ there's no support for curses' `A_STANDOUT` ("the best highlighting
mode available"), as it seems not to be mapped to a single escape sequence. On
Gnome Terminal, `A_STANDOUT` seems to be the same as `A_REVERSE`. If you're
interested in having this, open an issue and let's talk about it.

_Note 2:_ I plan on supporting italics (`\x1b[3m`, available in ECMA-48 and
xterm) in the future. If you're interested in having this, open an issue and
let's talk about it.

_Note 2:_ I plan to add support for italics (`\x1b[3m`, available in ECMA-48 and
xterm) in the future. If you're interested, open an issue and let's talk about
it.
