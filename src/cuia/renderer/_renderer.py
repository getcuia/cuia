"""A renderer protocol."""
from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from types import TracebackType
from typing import ContextManager, Iterator, Optional, Text, Type

from ..message import Message


@dataclass
class AbstractRenderer(ContextManager["AbstractRenderer"]):
    """Renderer protocol."""

    def __enter__(self) -> AbstractRenderer:
        """Enter context."""
        raise NotImplementedError()

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context."""
        raise NotImplementedError()

    @abstractmethod
    @contextmanager
    def into_raw_mode(self) -> Iterator[AbstractRenderer]:
        """Enter raw mode."""
        raise NotImplementedError()

    @abstractmethod
    def render(self, screen: Text) -> None:
        """Render a screen."""
        raise NotImplementedError()

    @abstractmethod
    def next_message(self) -> Optional[Message]:
        """Get next message."""
        raise NotImplementedError()
