"""Tests for the CursesRenderer class."""

from kay import color
from kay.renderer import CursesRenderer


def test_initial_colors():
    """Test that the curses renderer starts with the correct colors."""
    renderer = CursesRenderer()
    assert renderer.colors == {
        None: -1,
        color.BLACK: 0,
        color.RED: 1,
        color.GREEN: 2,
        color.YELLOW: 3,
        color.BLUE: 4,
        color.MAGENTA: 5,
        color.CYAN: 6,
        color.WHITE: 7,
    }
    assert renderer.color_pairs == {(None, None): -1, (color.WHITE, color.BLACK): 0}
