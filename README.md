[![PyPI](https://img.shields.io/pypi/v/cuia)](https://pypi.org/project/cuia/)
[![Python package](https://github.com/getcuia/cuia/actions/workflows/python-package.yml/badge.svg)](https://github.com/getcuia/cuia/actions/workflows/python-package.yml)
[![PyPI - License](https://img.shields.io/pypi/l/cuia)](https://github.com/getcuia/cuia/blob/main/LICENSE)

# [cuia](https://github.com/getcuia/cuia#readme) 🧉

<div align="center">
    <img class="hero" src="https://github.com/getcuia/cuia/raw/main/banner.svg" alt="cuia" width="33%" />
</div>

> A delightful tiny framework for building reliable text-based applications.

**cuia** is a tiny Python library for building interactive terminal user
interfaces that are easy to use, fast and have a small memory footprint.

cuia is inspired by [Bubble Tea](https://github.com/charmbracelet/bubbletea)
(written in [Go](https://golang.org/)) and, in particular, employs
[the Elm architecture](https://guide.elm-lang.org/architecture/) (TEA, named
after the [Elm programming language](https://elm-lang.org/)). This means that
**cuia applications are as dynamic and easy to write (and use) as they could
be**.

## Features

-   🧵 Simple: your user interface is a string of characters
-   💬 Interaction-focused
-   ♻️ Easily integrate with other libraries
-   🕹️ Use the same escape code sequences
    [as you would with Colorama](https://github.com/tartley/colorama#recognised-ansi-sequences)
-   🖥️ Support for Unix variants out of the box:
    [curses](https://docs.python.org/3/library/curses.html) under the hood by
    default (and probably works on Windows and DOS if a compatible curses
    library is available)
-   🤬 Only one dependency: [cusser](https://github.com/getcuia/cusser) (for
    wrapping the curses library)
-   🐍 Python 3.8+

## Installation

```console
$ pip install cuia
```

## Usage

```python
In [1]: import asyncio

In [2]: from dataclasses import dataclass

In [3]: from cuia import Program, Store

In [4]: @dataclass
   ...: class Hello(Store):
   ...:
   ...:     x: int = 0
   ...:     y: int = 0
   ...:
   ...:     def __str__(self):
   ...:         return f"\033[{self.x};{self.y}H\033[1mHello, 🌍!"
   ...:

In [5]: program = Program(Hello(34, 12))

In [6]: asyncio.run(program.start())

```

![Screenshot](https://github.com/getcuia/cuia/raw/main/screenshot.png)
