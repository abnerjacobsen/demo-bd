"""Test Snap App."""

import snap_backend_template


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(snap_backend_template.__name__, str)
