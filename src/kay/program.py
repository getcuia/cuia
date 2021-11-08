"""Program class."""


from __future__ import annotations

import asyncio
from asyncio import Queue
from dataclasses import dataclass
from typing import Optional

from kay.command import Command
from kay.message import Message, QuitMessage
from kay.model import Model
from kay.renderer.curses import CursesRenderer as Renderer


@dataclass
class Program:
    """Program class."""

    model: Model
    messages: Optional[Queue[Message]] = None
    commands: Optional[Queue[Command]] = None
    should_quit: bool = False
    # output: TextIO = sys.stdout
    # input: TextIO = sys.stdin

    async def start(self) -> None:
        """Start program."""
        with Renderer() as renderer:
            with renderer.into_raw_mode() as renderer:
                await self._start_impl(renderer)

    def init_queues(self) -> None:
        """Initialize queues."""
        self.messages = Queue()
        self.commands = Queue()

    async def enqueue_message(self, message: Optional[Message]) -> None:
        """Enqueue a message if not None."""
        if message:
            assert self.messages is not None, "Messages queue not initialized"
            await self.messages.put(message)

    async def enqueue_command(self, command: Optional[Command]) -> None:
        """Enqueue a command if not None."""
        if command:
            assert self.commands is not None, "Commands queue not initialized"
            await self.commands.put(command)

    def dequeue_message(self) -> Optional[Message]:
        """Get next message or return None."""
        try:
            assert self.messages is not None, "Messages queue not initialized"
            return self.messages.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def dequeue_command(self) -> Optional[Command]:
        """Get next command or return None."""
        try:
            assert self.commands is not None, "Commands queue not initialized"
            return self.commands.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def handle_message(self, message: Message) -> None:
        """Handle a message if it is not None."""
        if message:
            if isinstance(message, QuitMessage):
                self.should_quit = True

            # Update the model and maybe enqueue a command
            command = self.model.update(message)
            await self.enqueue_command(command)

    async def handle_command(self, command: Optional[Command]) -> None:
        """Handle a command if it is not None."""
        if command:
            # Run the command and maybe enqueue a message
            message = await command()
            await self.enqueue_message(message)

    async def _start_impl(self, renderer: Renderer):
        """Start program implementation."""
        # Queues have to be created inside the coroutine's event loop
        self.init_queues()

        # Get our first command
        command = self.model.init()
        await self.enqueue_command(command)

        while not self.should_quit:
            # It is important to show something on the screen as soon as possible
            view = self.model.view()
            await renderer.render(view)

            # Handle commands first because we might already have one at the beginning
            command = self.dequeue_command()
            await self.handle_command(command)

            # Now we expect the user to interact
            new_message = await renderer.next_message()
            await self.enqueue_message(new_message)

            # Finally, handle next message
            message = self.dequeue_message()
            await self.handle_message(message)
