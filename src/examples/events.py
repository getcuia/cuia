"""An example that shows all events on the screen."""

import asyncio
from dataclasses import dataclass
from typing import Optional, Text

import cuia


@dataclass
class EventfulExample(cuia.Store):
    """A store class that just prints all events."""

    last_message: Optional[cuia.Message] = None

    def update(self, message: cuia.Message) -> Optional[cuia.Command]:
        """Store the most recent message."""
        self.last_message = message
        return super().update(message)

    def __str__(self) -> Text:
        """Print the stored message."""
        return f"Last message: {self.last_message!r}"


async def main() -> None:
    """Run the application."""
    program = cuia.Program(EventfulExample())
    await program.start()


if __name__ == "__main__":
    asyncio.run(main())
