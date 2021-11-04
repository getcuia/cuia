"""🧓🏾🖥️ An old lady made a text-based app."""


__version__ = "0.1.0"
__all__ = [
    "Command",
    "quit",
    "Message",
    "KeyMessage",
    "QuitMessage",
    "Model",
    "Program",
]


from .command import Command, quit
from .message import KeyMessage, Message, QuitMessage
from .model import Model
from .program import Program
