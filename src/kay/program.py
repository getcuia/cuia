"""Program class."""


from __future__ import annotations
import asyncio

import curses
from asyncio import Queue
from dataclasses import dataclass
from typing import Optional

from kay.command import Command
from kay.message import Message
from kay.model import Model


@dataclass
class Program:
    """Program class."""

    model: Model
    messages: Optional[Queue[Message]] = None
    # output: TextIO = sys.stdout
    # input: TextIO = sys.stdin

    async def start(self):
        """Start program."""
        # Very similar to curses.wrapper
        try:
            stdscr = curses.initscr()
            curses.noecho()
            # curses.cbreak()
            stdscr.keypad(True)
            stdscr.nodelay(True)
            # try:
            #     curses.start_color()
            # except:
            #     pass

            return await self._start_impl(stdscr)
        finally:
            if "stdscr" in locals():
                stdscr.keypad(False)
                curses.echo()
                curses.nocbreak()
                curses.endwin()

    async def _start_impl(self, win: curses._CursesWindow):
        """Start program implementation."""
        # Queues have to be created inside the coroutine's event loop
        self.messages = Queue()
        commands: Queue[Command] = Queue()
        if (init_cmd := self.model.init()) is not None:
            await commands.put(init_cmd)

        while True:
            win.erase()
            win.addstr(self.model.view())
            win.refresh()
            await asyncio.sleep(1 / 60)

            # FIX: repeated from the beginning of the method
            if (message := Message.from_curses(win)) is not None:
                await self.messages.put(message)

            try:
                message = self.messages.get_nowait()
            except asyncio.QueueEmpty:
                continue

            # FIX: repeated from the beginning of the method
            if (cmd := self.model.update(message)) is not None:
                await commands.put(cmd)
