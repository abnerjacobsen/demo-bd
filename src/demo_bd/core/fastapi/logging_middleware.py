"""
Middleware for logging HTTP route access in FastAPI applications.

This module provides a Loguru-integrated middleware that logs request and response details,
handler information, and processing time for each route. It enhances observability and
debugging capabilities for FastAPI-based APIs.
"""

import functools
import inspect
import os
import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.routing import Route as StarletteRoute


class RouteAccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging access to each route.

    Logs request and response details, handler information, and processing time for each route.
    Integrates with Loguru for structured logging, providing enhanced observability for FastAPI applications.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """
        Handle the incoming request and log access details.

        Processes the request, logs access details including handler information and processing time,
        and returns the response. Integrates with Loguru for structured logging.
        """
        start_time = time.time()

        # Process the request first
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        # Extract handler/module/function/file/line info using helper
        (
            module_name,
            function_name,
            filename,
            pathname,
            lineno,
        ) = self._extract_handler_info(request)

        client_host = request.client.host if request.client else "unknown_client"
        url_path = request.url.path
        if request.url.query:
            url_path += "?" + request.url.query
        http_version = request.scope.get("http_version", "1.1")

        log_message = (
            f'{client_host} - "{request.method} {url_path} HTTP/{http_version}" '
            f"{response.status_code} ({process_time:.2f}ms)"
        )

        loguru_override_data = {
            "_log_record_original_name": module_name,
            "_log_record_original_filename": filename,
            "_log_record_original_pathname": pathname,
            "_log_record_original_lineno": lineno,
            "_log_record_original_funcName": function_name,
        }

        logger.bind(**loguru_override_data).info(log_message)
        return response

    def _extract_handler_info(self, request: Request):
        """Extract handler/module/function/file/line info for logging."""
        module_name = "unknown.module.mw_v2"
        function_name = "unknown.handler.mw_v2"
        filename = "unknown_file_mw_v2.py"
        pathname = "/unknown/path/unknown_file_mw_v2.py"
        lineno = 0

        actual_handler = None
        route_obj = request.scope.get("route")

        if isinstance(route_obj, StarletteRoute) and hasattr(route_obj, "endpoint"):
            actual_handler = route_obj.endpoint
            if isinstance(actual_handler, functools.partial):
                actual_handler = actual_handler.func
        else:
            actual_handler = request.scope.get("endpoint")
            if actual_handler and isinstance(actual_handler, functools.partial):
                actual_handler = actual_handler.func

        if actual_handler:
            if hasattr(actual_handler, "__module__"):
                module_name = actual_handler.__module__
            if hasattr(actual_handler, "__name__"):
                function_name = actual_handler.__name__

            code_object = getattr(actual_handler, "__code__", None)
            if code_object:
                pathname = code_object.co_filename
                filename = os.path.basename(pathname)
                lineno = code_object.co_firstlineno
            else:
                try:
                    pathname = inspect.getfile(actual_handler)
                    filename = os.path.basename(pathname)
                except (TypeError, OSError):
                    if module_name != "unknown.module.mw_v2":
                        filename = module_name.split(".")[-1] + ".py"
                        pathname = f"<{module_name.replace('.', '/')}/{filename}> (inferred)"
        return module_name, function_name, filename, pathname, lineno
