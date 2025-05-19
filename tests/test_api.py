"""Test Snap App REST API."""

import httpx
from fastapi.testclient import TestClient

from demo_bd.api import app

client = TestClient(app)


def test_read_root() -> None:
    """Test that reading the root is successful."""
    response = client.get("/v1/health/status")
    assert httpx.codes.is_success(response.status_code)
