"""A base class for all models."""


from abc import abstractmethod
from typing import Optional, Protocol

from kay.command import Command
from kay.event import Event


class Model(Protocol):
    """Model protocol."""

    @abstractmethod
    def update(self, event: Event) -> Optional[Command]:
        """Update the model with a message."""
        raise NotImplementedError()

    @abstractmethod
    def view(self) -> str:
        """Return a string representation of the model."""
        raise NotImplementedError()
