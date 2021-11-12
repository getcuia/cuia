"""Application commands."""


from typing import Awaitable, Callable, Optional

from . import message

Command = Callable[[], Awaitable[Optional[message.Message]]]


async def quit() -> Optional[message.Message]:
    """Signal to quit the application."""
    return message.QuitMessage()
