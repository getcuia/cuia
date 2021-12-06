"""A renderer wrapper that logs a program session to a file."""


from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Generic, Iterator, Optional, Text, Type, TypeVar

from ..messages import Event
from .renderer import Renderer

R = TypeVar("R", bound=Renderer)


@dataclass
class LogRenderer(Renderer, Generic[R]):
    """
    A renderer wrapper that logs a program session to a file.

    Examples
    --------
    >>> from cuia.renderer import CursesRenderer, LogRenderer
    >>> with LogRenderer(CursesRenderer()) as renderer:
    ...     renderer.render("Hello, world!")  # doctest: +SKIP
    """

    renderer: R
    path: Path = Path("log.txt")

    def __getattr__(self, name: Text):
        """Delegate all unknown attributes to the wrapped renderer."""
        return getattr(self.renderer, name)

    def render(self, screen: Text) -> None:
        """Render a screen."""
        return self.renderer.render(screen)

    def next_event(self) -> Optional[Event]:
        """Attempt to get the next terminal event."""
        return self.renderer.next_event()

    def __enter__(self) -> LogRenderer[R]:
        """Enter context."""
        self.renderer = self.renderer.__enter__()
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context."""
        return self.renderer.__exit__(exctype, excinst, exctb)

    @contextmanager
    def into_raw_mode(self) -> Iterator[LogRenderer[R]]:
        """Enter raw mode."""
        with self.renderer.into_raw_mode():
            yield self

    @contextmanager
    def hide_cursor(self) -> Iterator[LogRenderer[R]]:
        """Hide the cursor."""
        with self.renderer.hide_cursor():
            yield self
