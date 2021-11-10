"""Program class."""


from __future__ import annotations

import asyncio
from asyncio import Queue
from dataclasses import dataclass
from typing import Optional

from kay.command import Command
from kay.message import Message, QuitMessage
from kay.model import Model
from kay.renderer.curses import Renderer


@dataclass
class Program:
    """
    The program runtime.

    This object is responsible for properly running the program.
    """

    model: Model
    """The current state of the program."""
    messages: Optional[Queue[Message]] = None
    """The queue of messages to be handled."""
    commands: Optional[Queue[Command]] = None
    """The queue of commands to be handled."""
    should_render: bool = True
    """An indicator that the program should redraw the screen."""
    should_quit: bool = False
    """An indicator that the program should quit."""
    # output: TextIO = sys.stdout
    # input: TextIO = sys.stdin

    async def start(self) -> None:
        """Begin the program."""
        with Renderer() as renderer:
            with renderer.into_raw_mode() as renderer:
                await self._start_impl(renderer)

    def init_queues(self) -> None:
        """Initialize message and command queues."""
        self.messages = Queue()
        self.commands = Queue()

    async def enqueue_message(self, message: Message) -> None:
        """Enqueue a message to be handled later."""
        assert self.messages is not None, "Messages queue not initialized"
        await self.messages.put(message)

    async def enqueue_command(self, command: Command) -> None:
        """Enqueue a command to be handled later."""
        assert self.commands is not None, "Commands queue not initialized"
        await self.commands.put(command)

    def dequeue_message(self) -> Optional[Message]:
        """Get the next message if available, None otherwise."""
        try:
            assert self.messages is not None, "Messages queue not initialized"
            return self.messages.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def dequeue_command(self) -> Optional[Command]:
        """Get the next command if available, None otherwise."""
        try:
            assert self.commands is not None, "Commands queue not initialized"
            return self.commands.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def handle_message(self, message: Message) -> None:
        """Handle a message and update the model."""
        if isinstance(message, QuitMessage):
            self.should_quit = True

        # Update the model and maybe enqueue a command
        if command := self.model.update(message):
            await self.enqueue_command(command)

        # Remember to render the next time
        self.should_render = True

    async def handle_command(self, command: Command) -> None:
        """Handle a command and maybe enqueue an obtained message."""
        # Run the command and maybe enqueue a message
        if message := await command():
            await self.enqueue_message(message)

    async def _start_impl(self, renderer: Renderer):
        """
        Begin the program.

        This is the actual implementation of the `start` method.
        """
        # Queues have to be created inside the coroutine's event loop
        self.init_queues()

        # Get our first command
        if command := self.model.init():
            await self.enqueue_command(command)

        while not self.should_quit:
            # It is important to show something on the screen as soon as possible
            if self.should_render:
                view = self.model.view()
                renderer.render(view)
                self.should_render = False

            # Handle commands first because we might already have one at the beginning
            if command := self.dequeue_command():
                await self.handle_command(command)

            # Now we expect the user to interact
            if new_message := renderer.next_message():
                await self.enqueue_message(new_message)

            # Finally, handle next message
            if message := self.dequeue_message():
                await self.handle_message(message)
