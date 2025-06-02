"""Demo BD API HTTP routes."""

from fastapi import FastAPI

from demo_bd.routes.api.http.health.info import health_info_route, hello_word


def http_api_routers_include(app: FastAPI) -> None:
    """Include all HTTP API routes into the FastAPI app."""
    app.include_router(health_info_route)
    app.include_router(hello_word)


__all__ = [
    "http_api_routers_include",
]
