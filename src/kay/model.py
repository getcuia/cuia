"""A base class for all models."""


from abc import abstractmethod
from typing import Optional, Protocol

from kay.command import Command
from kay.message import Message


class Model(Protocol):
    """Model protocol."""

    @abstractmethod
    def init(self) -> Optional[Command]:
        """Return a command to initialize the model."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, message: Message) -> Optional[Command]:
        """Update the model with a message."""
        raise NotImplementedError()

    @abstractmethod
    def view(self) -> str:
        """Return a string representation of the model."""
        raise NotImplementedError()
