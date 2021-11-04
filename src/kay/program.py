"""Program class."""


from __future__ import annotations

import sys
from dataclasses import dataclass
from queue import Queue
from typing import TextIO

from kay.command import Command
from kay.message import Message
from kay.model import Model


@dataclass
class Program:
    """Program class."""

    model: Model
    messages: Queue[Message] = Queue()
    output: TextIO = sys.stdout
    input: TextIO = sys.stdin

    def start(self):
        """Start program."""
        commands: Queue[Command] = Queue()
        if (init_cmd := self.model.init()) is not None:
            commands.put(init_cmd)

        sys.stdout.write(self.model.view())
        print(sys.stdin.read())
