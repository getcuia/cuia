"""A renderer base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from types import TracebackType
from typing import ContextManager, Iterator, Optional, Text, Type, TypeVar

from ..message import Message

R = TypeVar("R", bound="Renderer")


@dataclass
class Renderer(ContextManager["Renderer"], ABC):
    """Renderer base class."""

    @abstractmethod
    def render(self, screen: Text) -> None:
        """Render a screen."""
        raise NotImplementedError("You must implement this method")

    @abstractmethod
    def next_message(self) -> Optional[Message]:
        """Get next message."""
        raise NotImplementedError("You must implement this method")

    @abstractmethod
    def __enter__(self: R) -> R:
        """
        Enter context.

        This should perform any setup required by the renderer.
        """
        raise NotImplementedError("You must implement this method")

    @abstractmethod
    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """
        Exit context.

        This should perform any teardown required by the renderer.
        """
        raise NotImplementedError("You must implement this method")

    @abstractmethod
    @contextmanager
    def into_raw_mode(self: R) -> Iterator[R]:
        """Enter raw mode."""
        raise NotImplementedError("You must implement this method")

    @abstractmethod
    @contextmanager
    def hide_cursor(self: R) -> Iterator[R]:
        """Hide the cursor."""
        raise NotImplementedError("You must implement this method")
