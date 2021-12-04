"""Tests for the program class."""

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


def test_program_creation() -> None:
    """Test program creation."""
    program = cuia.Program(Hello())

    assert isinstance(program.renderer, cuia.renderer.CursesRenderer)
    assert Text(program.store) == "Hello, world!"


def test_program_renderer() -> None:
    """Test giving a custom renderer to a program."""
    renderer = cuia.renderer.LogRenderer(cuia.renderer.CursesRenderer())
    program = cuia.Program(Hello(), renderer)

    assert isinstance(program.renderer, cuia.renderer.LogRenderer)
    assert Text(program.store) == "Hello, world!"
