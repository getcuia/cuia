"""🧓🏾🖥️ An old lady made a text-based app."""


__version__ = "0.1.0"
__all__ = ["Command", "quit", "Event", "KeyEvent", "QuitEvent", "Model", "Program"]


from .command import Command, quit
from .event import Event, KeyEvent, QuitEvent
from .model import Model
from .program import Program
