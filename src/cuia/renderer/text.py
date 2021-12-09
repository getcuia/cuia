"""A renderer that writes directly to the terminal."""


from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from types import TracebackType
from typing import Iterator, Optional, Text, Type

from ..messages import Event
from .renderer import Renderer

ORD_A = ord("a")


@dataclass
class TextRenderer(Renderer):
    """
    A renderer that writes directly to the terminal.

    Examples
    --------
    >>> with TextRenderer() as renderer:
    ...     renderer.render("Hello, world!")
    """

    def render(self, screen: Text) -> None:
        """Render a screen."""
        print(screen)

    def next_event(self) -> Optional[Event]:
        """Attempt to get the next terminal event."""
        # TODO: take a look at <https://stackoverflow.com/a/13207724/4039050> and
        # also <https://stackoverflow.com/a/47197390/4039050>. Bottom line: not that
        # hard at all.
        return None

    def __enter__(self) -> TextRenderer:
        """Enter context."""
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit context."""
        return None

    @contextmanager
    def into_raw_mode(self) -> Iterator[TextRenderer]:
        """Enter raw mode."""
        yield self

    @contextmanager
    def hide_cursor(self) -> Iterator[TextRenderer]:
        """Hide the cursor."""
        # TODO: in the future we may use an escape sequence for hiding the cursor
        yield self
