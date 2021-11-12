"""Application commands."""


from typing import Awaitable, Callable, Optional

from .message import Message, QuitMessage

Command = Callable[[], Awaitable[Optional[Message]]]


async def quit() -> Optional[Message]:
    """Signal to quit the application."""
    return QuitMessage()
