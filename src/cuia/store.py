"""A base class for storing application state."""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Text

from . import command
from .command import Command
from .messages import Key, Message


@dataclass  # type: ignore
class Store(ABC):
    """
    A base class for storing application state.

    Your application should extend this class and implement at least
    the `__str__` method (others are optional).
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
        but does nothing else other than that.
        """
        if isinstance(message, Key) and message in {Key.CTRL("c"), Key.CHAR("q")}:
            # The user pressed either Ctrl-C or Q, so we quit the application.
            return command.quit
        return None

    @abstractmethod
    def __str__(self) -> Text:
        """
        Render the store state as a string.

        You should override this method to implement the application's user interface.
        """
        raise NotImplementedError("You must implement this method")
