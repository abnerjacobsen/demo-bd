"""Test suite for the demo_bd FastAPI application API endpoints."""

import httpx
from fastapi.testclient import TestClient

from demo_bd.api import app
from demo_bd.core.config.settings import settings

client = TestClient(app)


def test_read_root() -> None:
    """Test that reading the root is successful, passando query params das configurações."""
    response = client.get(
        "/v1/health/status", params={settings.SECURITY.APIKEY_NAME: settings.SECURITY.APIKEY}
    )
    assert httpx.codes.is_success(response.status_code)
