"""A renderer wrapper that logs a program session to a file."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Iterator, Optional, Text, Type

from ..message import Message
from .renderer import Renderer


# TODO: make it generic
@dataclass
class LogRenderer(Renderer):
    """
    A renderer wrapper that logs a program session to a file.

    Examples
    --------
    >>> with LogRenderer() as renderer:
    ...     renderer.render("Hello, world!")  # doctest: +SKIP
    """

    renderer: Renderer
    path: Path = Path("log.txt")

    def __getattr__(self, name: Text):
        """Delegate all unknown attributes to the wrapped renderer."""
        return getattr(self.renderer, name)

    def render(self, screen: Text) -> None:
        """Render a screen."""
        return self.renderer.render(screen)

    def next_message(self) -> Optional[Message]:
        """Get next message."""
        return self.renderer.next_message()

    def __enter__(self) -> LogRenderer:
        """Enter context."""
        return self.renderer.__enter__()

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context."""
        return self.renderer.__exit__(exctype, excinst, exctb)

    @contextmanager
    def into_raw_mode(self) -> Iterator[LogRenderer]:
        """Enter raw mode."""
        with self.renderer.into_raw_mode():
            yield self

    @contextmanager
    def hide_cursor(self) -> Iterator[LogRenderer]:
        """Hide the cursor."""
        with self.renderer.hide_cursor():
            yield self
