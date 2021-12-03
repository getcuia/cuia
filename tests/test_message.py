"""Tests for messages."""


from typing import Text

import cuia


def test_quit_message():
    """Test quit message."""
    assert issubclass(cuia.Quit, cuia.Message)
    assert isinstance(cuia.Quit(), cuia.Message)


def test_key_message():
    """Test key message."""
    a = cuia.Key("a")
    assert issubclass(cuia.Key, cuia.Message)
    assert isinstance(a, cuia.Message)
    assert Text(a) == "a"
