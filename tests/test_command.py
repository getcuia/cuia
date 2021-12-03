"""Tests for commands."""

import asyncio

import cuia


def test_quit_command():
    """Test quit command."""
    assert isinstance(cuia.quit, cuia.Command)

    message = asyncio.run(cuia.quit())
    assert message == cuia.QuitMessage()
