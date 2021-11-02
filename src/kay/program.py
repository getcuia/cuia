"""Program class."""


from dataclasses import dataclass


from kay.model import Model


@dataclass
class Program:
    """Program class."""

    model: Model

    def start(self):
        """Start program."""
        pass
