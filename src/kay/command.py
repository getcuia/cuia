"""Application commands."""


from typing import Awaitable, Callable, Optional

from kay.message import Message, QuitMessage

Command = Callable[[], Awaitable[Optional[Message]]]


async def quit() -> Optional[Message]:
    """A command that signals to quit the application."""
    return QuitMessage()
