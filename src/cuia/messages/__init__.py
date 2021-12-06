"""Both terminal events and custom ones as message passing."""


from .event import Event, Key, KeyModifier, Resize, Unsupported
from .message import Message, Quit

__all__ = ["Event", "Key", "KeyModifier", "Message", "Quit", "Resize", "Unsupported"]
