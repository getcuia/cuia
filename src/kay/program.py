"""Program class."""


from __future__ import annotations

import sys
from dataclasses import dataclass
from queue import Queue
from typing import TextIO

from kay.command import Command
from kay.event import Event
from kay.model import Model


@dataclass
class Program:
    """Program class."""

    model: Model
    events: Queue[Event] = Queue()
    output: TextIO = sys.stdout
    input: TextIO = sys.stdin

    def start(self):
        """Start program."""
        commands: Queue[Command] = Queue()
        if (init_cmd := self.model.init()) is not None:
            commands.put(init_cmd)

        sys.stdout.write(self.model.view())
        print(sys.stdin.read())
