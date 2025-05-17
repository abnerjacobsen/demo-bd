"""Demo BD REST API."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import coloredlogs
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette_context import context, plugins
from starlette_context.middleware import ContextMiddleware

from demo_bd.core.config.settings import settings
from demo_bd.core.log.loguru_intercept_handling import setup_loguru_logging_intercept

setup_loguru_logging_intercept(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    modules=(
        "uvicorn.error",
        "uvicorn.asgi",
        "uvicorn.access",
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
    ),
)

print(settings)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle FastAPI startup and shutdown events."""
    logger.info("🚀 Starting application")
    # Startup events:
    # - Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    # - Add coloredlogs' colored StreamHandler to the root logger.
    coloredlogs.install()
    try:
        yield
        logger.info("⛔ Stopping application")
    finally:
        # Cleanup actions
        logger.info("✅ Application stopped")

    # Shutdown events.


app = FastAPI(lifespan=lifespan, title=settings.APP_TITLE, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["X-Requested-With", "X-Request-ID", "X-Correlation-ID"],
    expose_headers=["X-Request-ID", "X-Correlation-ID"],
)

app.add_middleware(
    ContextMiddleware,
    plugins=(
        plugins.RequestIdPlugin(force_new_uuid=False, validate=False),
        plugins.CorrelationIdPlugin(force_new_uuid=False, validate=False),
    ),
)


@app.get("/compute")
async def compute(n: int = 42) -> int:
    """Compute the result of a CPU-bound function.

    Returns
    -------
        int: fibonacci result
    """

    def fibonacci(n: int) -> int:
        return n if n <= 1 else fibonacci(n - 1) + fibonacci(n - 2)

    logger.info(context.get("X-Request-ID", None))
    result = await asyncio.to_thread(fibonacci, n)
    return result
