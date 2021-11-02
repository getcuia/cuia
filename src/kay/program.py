"""Program class."""


import sys
from dataclasses import dataclass
from queue import Queue
from typing import TextIO

from kay.model import Model


@dataclass
class Program:
    """Program class."""

    model: Model
    events: Queue = Queue()
    output: TextIO = sys.stdout
    input: TextIO = sys.stdin

    def start(self):
        """Start program."""
        pass
