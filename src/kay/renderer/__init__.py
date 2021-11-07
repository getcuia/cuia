"""A renderer protocol."""
from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from typing import ContextManager, Iterator, Optional, Protocol, Text, runtime_checkable

from kay.message import Message


@runtime_checkable
class Renderer(ContextManager, Protocol):
    """Renderer protocol."""

    def __enter__(self) -> Renderer:
        """Enter context."""
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def into_raw_mode(self) -> Iterator[Renderer]:
        """Enter raw mode."""
        raise NotImplementedError

    # TODO: this does not seem to need to be a coroutine
    @abstractmethod
    async def render(self, view: Text) -> None:
        """Render model."""
        raise NotImplementedError

    # TODO: this does not seem to need to be a coroutine
    @abstractmethod
    async def next_message(self) -> Optional[Message]:
        """Get next message."""
        raise NotImplementedError
