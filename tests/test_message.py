"""Tests for messages."""


import cuia
from cuia.messages import Event, Key, KeyModifier


def test_quit_message():
    """Test quit message."""
    assert issubclass(cuia.Quit, cuia.Message)
    assert isinstance(cuia.Quit(), cuia.Message)


def test_key_event_hierarchy():
    """Test key event hierarchy."""
    assert issubclass(Key, cuia.Message)
    assert issubclass(Key, Event)


def test_simple_key_event_message():
    """Test a simple key event message."""
    a = Key.CHAR("a")

    assert isinstance(a, cuia.Message)
    assert isinstance(a, Event)
    assert isinstance(a, Key)
    assert a.value == "a"
    assert a.modifier == KeyModifier.NONE


def test_key_event_with_modifier_message():
    """Test a key event with modifier message."""
    a = Key.ALT(Key.CTRL(Key.CHAR("a")))

    assert isinstance(a, cuia.Message)
    assert isinstance(a, Event)
    assert isinstance(a, Key)
    assert a.value == "a"
    assert a.modifier == KeyModifier.ALT | KeyModifier.CTRL
