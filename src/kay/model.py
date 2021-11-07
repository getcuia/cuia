"""A base class for all models."""


from abc import abstractmethod
from typing import Optional, Protocol, Text, runtime_checkable

from kay.command import Command, quit
from kay.message import KeyMessage, Message


@runtime_checkable
class Model(Protocol):
    """Model protocol."""

    def init(self) -> Optional[Command]:
        """
        Return a command to initialize the model.

        The default implementation does nothing and always returns None.
        """
        return None

    def update(self, message: Message) -> Optional[Command]:
        """
        Update the model with a message and possibly return a command.

        The default implementation terminates the program if the user presses Ctrl-C,
        otherwise it does nothing.
        """
        if isinstance(message, KeyMessage):
            if Text(message) == "ctrl+c":
                return quit
        return None

    @abstractmethod
    def view(self) -> Text:
        """
        Return a textual representation of the model.

        This is required to be implemented by subclasses.
        """
        raise NotImplementedError()
