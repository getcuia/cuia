"""General tests for the kay package."""

from kay import __version__


def test_version() -> None:
    """Test the version of the package."""
    assert __version__ == "0.1.0"
