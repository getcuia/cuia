"""Program class."""


import sys
from dataclasses import dataclass
from typing import TextIO

from kay.model import Model


@dataclass
class Program:
    """Program class."""

    model: Model
    output: TextIO = sys.stdout
    input: TextIO = sys.stdin

    def start(self):
        """Start program."""
        pass
