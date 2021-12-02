"""
Show a greeting to the user.

This example is based on the Elm example at: <https://elm-lang.org/examples/hello>.
"""


import asyncio
from dataclasses import dataclass

import cuia


@dataclass
class Hello(cuia.Store):
    """An application that greets the user."""

    def __str__(self):
        """Render our greeting."""
        return "\033[1mHello!"


if __name__ == "__main__":
    asyncio.run(cuia.Program(Hello()).start())
