"""
Application commands.

Commands are ways of delegating work to the runtime environment so that things can
run asynchronously, not blocking the main thread, and yet be easy to code and test.
"""


from typing import Awaitable, Callable, Optional

from .message import Message, QuitMessage

Command = Callable[[], Awaitable[Optional[Message]]]


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
    return QuitMessage()
