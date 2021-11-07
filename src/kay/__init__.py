"""🧓🏾🖥️ An old lady made a text-based app."""


__version__ = "0.1.0"
__all__ = [
    "Attr",
    "Background",
    "Color",
    "Command",
    "Foreground",
    "KeyMessage",
    "Message",
    "Model",
    "Program",
    "quit",
    "QuitMessage",
]


from .attr import Attr
from .color import Background, Color, Foreground
from .command import Command, quit
from .message import KeyMessage, Message, QuitMessage
from .model import Model
from .program import Program
