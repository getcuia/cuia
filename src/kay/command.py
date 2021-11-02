"""Application commands."""


from typing import Callable, Optional

from kay.event import Event, QuitEvent

Command = Callable[[], Optional[Event]]


def quit() -> Optional[Event]:
    """Signal to quit the application."""
    return QuitEvent()
