"""Application commands."""


from typing import Callable, Optional

from kay.message import Message, QuitMessage

Command = Callable[[], Optional[Message]]


def quit() -> Optional[Message]:
    """Signal to quit the application."""
    return QuitMessage()
