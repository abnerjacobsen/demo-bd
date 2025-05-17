"""Code to integrate Loguru with Python's standard logging module.

Comes from: https://github.com/MatthewScholefield/loguru-logging-intercept
https://github.com/doctor3030/loguru-logger-lite/tree/master
https://github.com/erezinman/loguru-config
https://github.com/pahntanapat/Unified-FastAPI-Gunicorn-Log
https://github.com/kaxiluo/fastapi-skeleton/tree/master
https://github.com/ManoManoTech/loggia
"""

import logging
import os
import platform
from itertools import chain
from pprint import pformat
from sys import stdout
from types import FrameType
from typing import cast

import pendulum
import stackprinter
from loguru import logger
from starlette_context import context

# from src.app.middlewares.request_id import request_id_context


def set_log_extras(record):
    """set_log_extras [summary].

    [extended_summary]

    Args:
        record ([type]): [description]
    """
    record["extra"]["datetime"] = pendulum.now("UTC")
    record["extra"]["host"] = os.getenv(
        "HOSTNAME", os.getenv("COMPUTERNAME", platform.node())
    ).split(".")[0]
    record["extra"]["pid"] = os.getpid()
    if context.exists():
        record["extra"]["correlation_id"] = context.get("X-Correlation-ID", None)
        record["extra"]["request_id"] = context.get("X-Request-ID", None)
    else:
        record["extra"]["correlation_id"] = None
        record["extra"]["request_id"] = None
    # record["extra"]["request_id"] = request_id_context.get()
    record["extra"]["app_name"] = "app"  # settings.PROJECT_NAME


def format_exception(exc_info):
    """Format an exception using stackprinter for enhanced readability.

    Args:
        exc_info: Exception info tuple as returned by sys.exc_info().

    Returns
    -------
        str: Formatted and indented exception traceback.
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
    """Return an custom format for loguru loggers.

    Uses pformat for log any data like request/response body
    [   {   'count': 2,
            'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
                         {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    format_string = "<green>{extra[datetime]}</green> | "
    format_string += "<green>{extra[app_name]}</green> | "
    format_string += "<green>{extra[host]}</green> | "
    format_string += "<green>{extra[pid]}</green> | "
    format_string += "<white>{extra[correlation_id]}</white> | "
    format_string += "<blue>{extra[request_id]}</blue> | "
    format_string += "<level>{level: <8}</level> | "
    format_string += "<cyan>{name}</cyan>:"
    format_string += "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    format_string += "<level>{message}</level>"

    # Dynamically format any extra fields, including payload
    for key, value in record["extra"].items():
        if key not in {
            "datetime",
            "app_name",
            "host",
            "pid",
            "correlation_id",
            "request_id",
        }:
            if not isinstance(value, str):
                record["extra"][key] = pformat(value, indent=4, compact=True, width=88)
            format_string += f"\n<level>{key}:\n{{extra[{key}]}}</level>"

    # This is to nice print data, like:
    # logger.bind(payload=dataobject).info("Received data")
    # if record["extra"].get("payload") is not None:
    #     if not isinstance(record["extra"]["payload"], str):
    #         record["extra"]["payload"] = pformat(
    #             record["extra"]["payload"], indent=4, compact=True, width=88
    #         )
    #     format_string += "\n<level>{extra[payload]}</level>"

    if record["exception"] is not None:
        # record["extra"]["stack"] = stackprinter.format(
        #     record["exception"], style="darkbg2", show_vals="all"
        # )
        record["extra"]["stack"] = format_exception(exc_info=record["exception"])

        format_string += "\n{extra[stack]}"
        # if record["exception"].type is types.TracebackType:
        #     record["exception"].value = None
    # format_string += "{exception}\n"

    format_string += "\n"
    return format_string


class InterceptHandler(logging.Handler):
    """Logs to loguru from Python logging module."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Loguru, mapping standard logging records."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def setup_loguru_logging_intercept(level=logging.DEBUG, modules=()):
    logging.basicConfig(handlers=[InterceptHandler()], level=level)
    for logger_name in chain(("",), modules):
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler(level=level)]
        mod_logger.propagate = False
    logger.configure(
        handlers=[
            {
                "sink": stdout,
                # https://loguru.readthedocs.io/en/stable/api/logger.html#sink
                # "sink": "./somefile.log",
                # "rotation": "10 MB",
                "serialize": False,
                "format": format_record,
                "diagnose": True,
                "backtrace": True,
                "enqueue": False,
            }
        ]
    )
    logger.configure(patcher=set_log_extras)
