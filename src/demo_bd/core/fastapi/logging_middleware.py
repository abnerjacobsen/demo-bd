import functools
import inspect
import os
import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.routing import Route as StarletteRoute


class RouteAccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start_time = time.time()

        # Processa a requisição PRIMEIRO
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        # AGORA, tenta ler o scope, depois que a rota foi processada internamente
        module_name = "unknown.module.mw_v2"
        function_name = "unknown.handler.mw_v2"
        filename = "unknown_file_mw_v2.py"
        pathname = "/unknown/path/unknown_file_mw_v2.py"
        lineno = 0

        actual_handler = None
        route_obj = request.scope.get("route")  # Tenta ler o scope AQUI

        # print(f"DEBUG MW_V2: Request Path: {request.url.path}")
        # print(
        #     f"DEBUG MW_V2: request.scope.get('route') AFTER call_next = {route_obj} (type: {type(route_obj)})"
        # )

        if isinstance(route_obj, StarletteRoute) and hasattr(route_obj, "endpoint"):
            actual_handler = route_obj.endpoint
            # print(
            #     f"DEBUG MW_V2: Found route.endpoint: {actual_handler} (type: {type(actual_handler)})"
            # )
            if isinstance(actual_handler, functools.partial):
                actual_handler = actual_handler.func
                # print(
                #     f"DEBUG MW_V2: Unwrapped functools.partial to: {actual_handler} (type: {type(actual_handler)})"
                # )
        else:
            actual_handler = request.scope.get("endpoint")  # Tenta ler o scope AQUI
            # print(
            #     f"DEBUG MW_V2: Falling back to request.scope.get('endpoint') AFTER call_next: {actual_handler} (type: {type(actual_handler)})"
            # )
            if actual_handler and isinstance(actual_handler, functools.partial):
                actual_handler = actual_handler.func
                # print(
                #     f"DEBUG MW_V2: Fallback: Unwrapped functools.partial to: {actual_handler} (type: {type(actual_handler)})"
                # )

        if actual_handler:
            # print(f"DEBUG MW_V2: Processing actual_handler: {actual_handler}")
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
        # else:
        #     print(
        #         f"DEBUG MW_V2: actual_handler is None or not found AFTER call_next. Default values will be used."
        #     )

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
