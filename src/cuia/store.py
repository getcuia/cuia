"""A base class for all stores."""


from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Text

from . import command
from .command import Command
from .message import Key, Message


# TODO: make this an abstract class
@dataclass
class Store:
    """
    A simple store base class.

    Your application should extend this class and implement at least the
    `__str__` method.
    """

    def start(self) -> Optional[Command]:
        """
        Return a command to initialize the store state.

        You can override this method to pass a command at startup.
        The default implementation does nothing (always returns None).
        """
        return None

    def update(self, message: Message) -> Optional[Command]:
        """
        Update the store state with a message and possibly return a command.

        You can override this method to implement the actual application logic.
        The default implementation terminates the program if the user presses Ctrl-C,
        but does nothing else.
        """
        if isinstance(message, Key) and Text(message) == "ctrl+c":
            # The user pressed Ctrl-C, so we quit the application.
            return command.quit
        return None

    @abstractmethod
    def __str__(self) -> Text:
        """
        Render the store state as a string.

        You should override this method to implement the application's user interface.
        """
        raise NotImplementedError()
