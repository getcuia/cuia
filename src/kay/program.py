"""Program class."""


from __future__ import annotations

import asyncio
from asyncio import Queue
from dataclasses import dataclass
from typing import Optional

from kay.command import Command
from kay.message import Message, QuitMessage
from kay.model import Model
from kay.renderer import CursesRenderer as Renderer


@dataclass
class Program:
    """Program class."""

    model: Model
    messages: Optional[Queue[Message]] = None
    # output: TextIO = sys.stdout
    # input: TextIO = sys.stdin

    async def start(self) -> None:
        """Start program."""
        with Renderer() as renderer:
            with renderer.into_raw_mode() as renderer:
                await self._start_impl(renderer)

    async def _start_impl(self, renderer: Renderer):
        """Start program implementation."""
        # Queues have to be created inside the coroutine's event loop
        self.messages = Queue()
        commands: Queue[Command] = Queue()
        if (init_cmd := self.model.init()) is not None:
            await commands.put(init_cmd)

        while True:
            await renderer.render(self.model.view())

            # Deal with commands first because we might have received a command right
            # after starting the program
            try:
                if (cmd := commands.get_nowait()) is not None:
                    if (message := cmd()) is not None:
                        if isinstance(message, QuitMessage):
                            break
                        await self.messages.put(message)
            except asyncio.QueueEmpty:
                pass

            # Then wait for input from the user
            # FIX: repeated from the beginning of the method
            if (message := await renderer.next_message()) is not None:
                await self.messages.put(message)

            try:
                message = self.messages.get_nowait()
            except asyncio.QueueEmpty:
                pass

            # And finally, update the model
            if (cmd := self.model.update(message)) is not None:
                await commands.put(cmd)
