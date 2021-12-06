"""Both terminal events and custom ones as message passing."""


from .event import Event, Key, KeyModifier, Unsupported
from .message import Message, Quit

__all__ = ["Event", "Key", "KeyModifier", "Message", "Quit", "Unsupported"]
