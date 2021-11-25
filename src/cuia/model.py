"""A base class for all models."""


from abc import abstractmethod
from typing import Optional, Protocol, Text, runtime_checkable

from .command import Command
from .message import Key, Message


@runtime_checkable
class Model(Protocol):
    """
    A simple model protocol.

    Your application should implement this protocol.
    """

    def start(self) -> Optional[Command]:
        """
        Return a command to initialize the model.

        You can override this method to pass a command at startup.
        The default implementation does nothing and always returns None.
        """
        return None

    def update(self, message: Message) -> Optional[Command]:
        """
        Update the model with a message and possibly return a command.

        You can override this method to implement the actual application logic.
        The default implementation terminates the program if the user presses Ctrl-C,
        otherwise it does nothing.
        """
        if isinstance(message, Key):
            if Text(message) == "ctrl+c":
                return quit
        return None

    @abstractmethod
    def view(self) -> Text:
        """
        Return a textual representation of the model.

        You should override this method to implement the application's
        view representation.
        """
        raise NotImplementedError()
