"""Application commands."""


from abc import abstractmethod
from typing import Optional, Protocol, runtime_checkable

from .messages import Message, Quit


@runtime_checkable
class Command(Protocol):
    """
    Command interface.

    Commands are ways of delegating work to the runtime environment so that things can
    run asynchronously, not blocking the main thread, and yet be easy to code and test.
    """

    @abstractmethod
    async def __call__(self) -> Optional[Message]:
        """
        Execute the command.

        It returns the message to send to the client, or None if no message should
        be sent.
        """
        raise NotImplementedError("Command must be callable")


async def quit() -> Optional[Message]:
    """
    Signal a message to the application that it should quit.

    Notes
    -----
    This conflicts with the standard `quit` function, so it is recommended to
    import it qualified. See the example below.

    Examples
    --------
    >>> # from cuia import quit  # Don't do this
    >>> import cuia              # Do this instead
    >>> cuia.quit
    <function quit at 0x...>
    """
    return Quit()
