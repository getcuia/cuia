"""
> A delightful tiny framework for building reliable text-based applications.

**cuia** is a tiny Python library for building interactive terminal user
interfaces that are easy to use, fast and have a small memory footprint.
"""


__version__ = "0.1.0"


from .command import Command, quit
from .messages import Key, Message, Quit
from .program import Program
from .store import Store

__all__ = ["Command", "Key", "Message", "Program", "quit", "Quit", "Store"]
