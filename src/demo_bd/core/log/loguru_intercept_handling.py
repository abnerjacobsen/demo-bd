"""Loguru intercept handling utilities for enhanced logging integration.

This module provides functions and classes to intercept standard logging and route it through Loguru,
enriching log records with contextual information and custom formatting.
"""

import logging
import os
import platform
from collections import namedtuple
from collections.abc import Iterable
from itertools import chain
from pprint import pformat
from sys import stdout
from typing import Any, cast

import pendulum
import stackprinter
from loguru import logger
from starlette_context import context

_LoguruFileRecord = namedtuple("_LoguruFileRecord", ["name", "path"])


def set_log_extras(record):
    """
    Set extra fields in the log record for Loguru.

    This function ensures that certain contextual fields (datetime, host, pid, correlation_id,
    request_id, app_name, etc.) are present in the log record's 'extra' dictionary. It also
    restores original log record attributes if present.

    Args:
        record (dict): The log record to update.
    """
    if "datetime" not in record["extra"]:
        record["extra"]["datetime"] = pendulum.now("UTC")
    if "host" not in record["extra"]:
        record["extra"]["host"] = os.getenv(
            "HOSTNAME", os.getenv("COMPUTERNAME", platform.node())
        ).split(".")[0]
    if "pid" not in record["extra"]:
        record["extra"]["pid"] = os.getpid()

    if context.exists():
        record["extra"].setdefault("correlation_id", context.get("X-Correlation-ID", None))
        record["extra"].setdefault("request_id", context.get("X-Request-ID", None))
    else:
        record["extra"].setdefault("correlation_id", None)
        record["extra"].setdefault("request_id", None)

    record["extra"].setdefault("app_name", "app")

    if "_log_record_original_name" in record["extra"]:
        original_logger_name = record["extra"].pop("_log_record_original_name")
        original_filename = record["extra"].pop("_log_record_original_filename")
        original_pathname = record["extra"].pop("_log_record_original_pathname")
        original_lineno = record["extra"].pop("_log_record_original_lineno")
        original_func_name = record["extra"].pop("_log_record_original_funcName")

        record["name"] = original_logger_name
        record["file"] = _LoguruFileRecord(name=original_filename, path=original_pathname)
        record["line"] = original_lineno
        record["function"] = original_func_name

        if record["name"] is None:
            record["module"] = None
        else:
            parts = record["name"].rsplit(".", 1)
            record["module"] = parts[0] if len(parts) > 1 else record["name"]


def format_exception(exc_info):
    """
    Format an exception using stackprinter and return an indented string.

    Args:
        exc_info: Exception info tuple as returned by sys.exc_info().

    Returns
    -------
        str: The formatted and indented exception string.
    """
    msg = stackprinter.format(
        exc_info,
        style="darkbg2",
        show_vals="all",
        suppressed_paths=[
            r"lib/python.*/site-packages/starlette",
            r"lib/python.*/site-packages/uvicorn",
        ],
    )
    lines = msg.split("\n")
    lines_indented = ["  ┆ " + line + "\n" for line in lines]
    msg_indented = "".join(lines_indented)
    return msg_indented


def format_record(record: dict) -> str:
    """
    Format a log record for Loguru output.

    Args:
        record (dict): The log record to format.

    Returns
    -------
        str: The formatted log record string.
    """
    format_string = "<green>{extra[datetime]}</green> | "
    format_string += "<green>{extra[app_name]}</green> | "
    format_string += "<green>{extra[host]}</green> | "
    format_string += "<green>{extra[pid]}</green> | "
    format_string += "<white>{extra[correlation_id]}</white> | "
    format_string += "<blue>{extra[request_id]}</blue> | "
    format_string += "<level>{level: <8}</level> | "
    format_string += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    format_string += "<level>{message}</level>"
    for key, value in record["extra"].items():
        if key not in {"datetime", "app_name", "host", "pid", "correlation_id", "request_id"}:
            if not isinstance(value, str):
                record["extra"][key] = pformat(value, indent=4, compact=True, width=88)
            format_string += f"\n<level>{key}:\n{{extra[{key}]}}</level>"
    if record["exception"] is not None:
        record["extra"]["stack"] = format_exception(exc_info=record["exception"])
        format_string += "\n{extra[stack]}"
    format_string += "\n"
    return format_string


class InterceptHandler(logging.Handler):
    """
    Logging handler that intercepts standard logging records and routes them through Loguru.

    Optionally ignores specified logger names to prevent interception.
    """

    def __init__(self, level: int = 0, ignore_loggers: Iterable[str] | None = None):
        super().__init__(level)
        self.ignore_loggers = set(ignore_loggers) if ignore_loggers else set()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a logging record, routing it through Loguru unless the logger is ignored.

        Args:
            record (logging.LogRecord): The log record to be handled.
        """
        if record.name in self.ignore_loggers:
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        loguru_override_data = {
            "_log_record_original_name": record.name,
            "_log_record_original_filename": record.filename,
            "_log_record_original_pathname": record.pathname,
            "_log_record_original_lineno": record.lineno,
            "_log_record_original_funcName": record.funcName,
        }

        logger_with_context = logger.bind(**loguru_override_data)
        logger_with_context.opt(depth=0, exception=record.exc_info).log(level, record.getMessage())


def setup_loguru_logging_intercept(
    level: int = logging.DEBUG,
    modules: Iterable[str] | None = None,
    ignore_intercept_loggers: Iterable[str] | None = None,
):
    """
    Set up Loguru to intercept and handle standard logging module logs.

    This function configures the logging system to route logs from the standard
    logging module through Loguru, applying custom formatting and context.

    Args:
        level (int): The minimum logging level to capture (default: logging.DEBUG).
        modules (Iterable[str] | None): Specific logger names to intercept. If None, applies to root and all modules.
        ignore_intercept_loggers (Iterable[str] | None): Logger names to ignore for interception.
    """
    modules_to_configure = () if modules is None else modules

    intercept_handler = InterceptHandler(ignore_loggers=ignore_intercept_loggers)

    logging.basicConfig(handlers=[intercept_handler], level=level)

    for logger_name in chain(("",), modules_to_configure):
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [intercept_handler]
        mod_logger.propagate = False

    handler_config: dict[str, Any] = {
        "sink": stdout,
        "serialize": False,
        "format": format_record,  # Certifique-se que format_record está corretamente tipado
        "diagnose": True,
        "backtrace": True,
        "enqueue": False,
    }

    logger.configure(
        handlers=cast(list[Any], [handler_config]),  # <<< MODIFICADO AQUI
        patcher=set_log_extras,  # Certifique-se que set_log_extras está corretamente tipado
    )
