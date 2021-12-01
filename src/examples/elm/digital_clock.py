"""
Show the current time in your time zone.

This example is based on the Elm example at: <https://elm-lang.org/examples/time>.
"""


import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Text

import pyfiglet  # type: ignore

import cuia


@dataclass
class TickMessage(cuia.Message):
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
class Model(cuia.Model):
    """The model for the application."""

    time: datetime

    def start(self) -> Optional[cuia.Command]:
        """Initialize the model."""
        return tick

    def update(self, message: cuia.Message) -> Optional[cuia.Command]:
        """Update the model based on the message received."""
        if isinstance(message, TickMessage):
            self.time = message.time
            return tick
        if isinstance(message, cuia.Key):
            if message.key == "ctrl+c":
                return cuia.quit
        return None

    def view(self) -> Text:
        """Render the view."""
        clock = pyfiglet.figlet_format(self.time.strftime("%H:%M:%S"))
        return f"{Attr.BOLD}{clock}{Attr.NORMAL}"


async def main() -> None:
    """Run the application."""
    program = cuia.Program(Model(datetime.now()))
    await program.start()


if __name__ == "__main__":
    asyncio.run(main())
