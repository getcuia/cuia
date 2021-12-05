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


@dataclass(frozen=True)
class TickMessage(cuia.Message):
    """A message informing the tick of the clock."""

    time: datetime


async def tick() -> Optional[TickMessage]:
    """
    Tick the clock.

    This won't block the main loop.
    """
    await asyncio.sleep(1)
    return TickMessage(datetime.now())


@dataclass
class DigitalClock(cuia.Store):
    """The store for our digital clock."""

    time: datetime

    def start(self) -> Optional[cuia.Command]:
        """Initialize the ticking."""
        return tick

    def update(self, message: cuia.Message) -> Optional[cuia.Command]:
        """Update the clock state based on the message received."""
        if isinstance(message, TickMessage):
            self.time = message.time
            return tick
        return super().update(message)

    def __str__(self) -> Text:
        """Render the digital clock as a string."""
        clock = pyfiglet.figlet_format(self.time.strftime("%H:%M:%S"))
        return f"\033[1m{clock}\033[0m"


async def main() -> None:
    """Run the application."""
    program = cuia.Program(DigitalClock(datetime.now()))
    await program.start()


if __name__ == "__main__":
    asyncio.run(main())
