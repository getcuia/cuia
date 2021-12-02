"""Program class."""


from __future__ import annotations

import asyncio
from asyncio import Queue
from dataclasses import dataclass
from typing import Optional, Type

from stransi import Ansi

from .command import Command
from .message import Message, QuitMessage
from .renderer import Renderer, curses
from .store import Store


@dataclass
class Program:
    """
    The program runtime.

    This object is responsible for properly running the program.

    Examples
    --------
    >>> class Hello(Store):
    ...     def start(self) -> Optional[Command]:
    ...         return quit
    ...     def __str__(self) -> Text:
    ...         return "Hello, world!"
    >>> program = Program(Hello())
    >>> asyncio.run(program.start())  # doctest: +SKIP
    """

    store: Store
    """The current state of the program."""
    messages: Optional[Queue[Message]] = None
    """The queue of messages to be handled."""
    should_render: bool = True
    """An indicator that the program should redraw the screen."""
    should_quit: bool = False
    """An indicator that the program should quit."""
    renderer: Type[Renderer] = curses.CursesRenderer
    # output: TextIO = sys.stdout
    # input: TextIO = sys.stdin

    async def start(self) -> None:
        """Begin the program."""
        with self.renderer() as renderer:
            with renderer.into_raw_mode() as renderer:
                # Queues have to be created inside the coroutine's event loop
                self.messages = Queue()

                # Get our first command
                if command := self.store.start():
                    await self.obey(command)

                while not self.should_quit:
                    # Show something to the screen as soon as possible
                    if self.should_render:
                        renderer.render(Ansi(self.store))
                        self.should_render = False

                    # Expect the user to interact
                    if new_message := renderer.next_message():
                        await self.enqueue_message(new_message)

                    # Handle a next message if available
                    if message := self.dequeue_message():
                        await self.handle_message(message)

                    # TODO: should we sleep here?
                    await asyncio.sleep(1 / 60)

    async def obey(self, command: Command) -> None:
        """
        Spawn a concurrent task to await the command's result.

        If the command produces a message, it is enqueued for later handling.
        """

        async def handler() -> None:
            # Await the command and maybe enqueue a message
            if message := await command():
                await self.enqueue_message(message)

        # Spawn the task to run the command
        asyncio.create_task(handler())

    async def enqueue_message(self, message: Message) -> None:
        """Enqueue a message to be handled later."""
        assert self.messages is not None, "Messages queue not initialized"
        await self.messages.put(message)

    def dequeue_message(self) -> Optional[Message]:
        """Get the next message if available, None otherwise."""
        assert self.messages is not None, "Messages queue not initialized"
        try:
            return self.messages.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def handle_message(self, message: Message) -> None:
        """Handle a message and update the store state."""
        if isinstance(message, QuitMessage):
            self.should_quit = True

        # Update the store state and maybe obey a command
        if command := self.store.update(message):
            await self.obey(command)

        # Remember to render the next time
        self.should_render = True
