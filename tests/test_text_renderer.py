"""Tests for the text renderer."""


from typing import Optional, Text

import cuia


class Hello(cuia.Store):
    """A program that produces 'Hello, world!' and exits."""

    def start(self) -> Optional[cuia.Command]:
        """Exit immediately."""
        return quit

    def __str__(self) -> Text:
        """Return 'Hello, world!'."""
        return "Hello, world!"


def test_renderer() -> None:
    """Test giving a custom renderer to a program."""
    program = cuia.Program(Hello(), cuia.renderer.TextRenderer())

    assert isinstance(program.renderer, cuia.renderer.TextRenderer)
    assert Text(program.store) == "Hello, world!"
