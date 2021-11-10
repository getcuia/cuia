"""
Show the current time in your time zone.

This example is based on the Elm example at: <https://elm-lang.org/examples/time>.
"""


import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Text

import pyfiglet  # type: ignore

import kay
from kay import Attr


@dataclass
class TickMessage(kay.Message):
    """A message to tick the model."""

    time: datetime


async def tick() -> Optional[TickMessage]:
    """
    Tick the model.

    This won't block the main loop.
    """
    await asyncio.sleep(1)
    return TickMessage(datetime.now())


@dataclass
class Model(kay.Model):
    """The model for the application."""

    time: datetime

    def init(self) -> Optional[kay.Command]:
        """Initialize the model."""
        return tick

    def update(self, message: kay.Message) -> Optional[kay.Command]:
        """Update the model based on the message received."""
        if isinstance(message, TickMessage):
            self.time = message.time
            return tick
        if isinstance(message, kay.KeyMessage):
            if message.key == "ctrl+c":
                return kay.quit
        return None

    def view(self) -> Text:
        """Render the view."""
        clock = pyfiglet.figlet_format(self.time.strftime("%H:%M:%S"), font="lcd")
        return f"{Attr.BOLD}{clock}{Attr.NORMAL}"


async def main() -> None:
    """Run the application."""
    program = kay.Program(Model(datetime.now()))
    try:
        await program.start()
    except Exception as err:
        # It is a good idea to narrow down the error type in production code.
        print(f"Alas, there's been an error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
