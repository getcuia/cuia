"""Tests for messages."""


import cuia


def test_quit_message():
    """Test quit message."""
    assert issubclass(cuia.Quit, cuia.Message)
    assert isinstance(cuia.Quit(), cuia.Message)


def test_key_message():
    """Test key message."""
    a = cuia.Key.CHAR("a")

    assert isinstance(a, cuia.Key)
    assert a.data == "a"

    assert issubclass(cuia.Key, cuia.Message)
    assert isinstance(a, cuia.Message)
