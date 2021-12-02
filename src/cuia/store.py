"""A base class for all stores."""


from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Text

from .command import Command
from .message import Key, Message


# TODO: make this an abstract class
@dataclass
class Store:
    """
    A simple store protocol.

    Your application should implement this protocol.
    """

    def start(self) -> Optional[Command]:
        """
        Return a command to initialize the store.

        You can override this method to pass a command at startup.
        The default implementation does nothing and always returns None.
        """
        return None

    def update(self, message: Message) -> Optional[Command]:
        """
        Update the store with a message and possibly return a command.

        You can override this method to implement the actual application logic.
        The default implementation terminates the program if the user presses Ctrl-C,
        otherwise it does nothing.
        """
        if isinstance(message, Key):
            if Text(message) == "ctrl+c":
                # BUG: not working
                return quit
        return None

    @abstractmethod
    def __str__(self) -> Text:
        """
        Return a textual representation of the store.

        You should override this method to implement the application's user interface.
        """
        raise NotImplementedError()
