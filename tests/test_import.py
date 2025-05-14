"""Test Snap App."""

import demo_bd


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(demo_bd.__name__, str)
