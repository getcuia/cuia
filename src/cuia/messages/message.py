"""Generic messages."""


from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class Message(ABC):
    """
    Simple message base class.

    This is a kind of a
    [marker interface](https://en.wikipedia.org/wiki/Marker_interface_pattern).
    Subclass this to create custom messages. There are no requirements for
    custom messages, but subclassing ensures that messages can be identified
    by the runtime and handled correctly.
    """


@dataclass(frozen=True)
class Quit(Message):
    """A message informing the application to quit."""
