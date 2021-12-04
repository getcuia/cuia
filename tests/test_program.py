"""Tests for the program class."""

from typing import Optional, Text

import cuia


class Hello(cuia.Store):
    def start(self) -> Optional[cuia.Command]:
        return quit

    def __str__(self) -> Text:
        return "Hello, world!"


def test_program_creation() -> None:
    """Test the program start method."""
    program = cuia.Program(Hello())

    assert program.renderer == cuia.renderer.CursesRenderer
    assert Text(program.store) == "Hello, world!"
