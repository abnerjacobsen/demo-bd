import pendulum
from fastapi import APIRouter, Depends, status
from fastapi_problem_details import ProblemException

from demo_bd.core.config.settings import settings
from demo_bd.core.fastapi.apikey import make_api_key_dependency
from demo_bd.core.fastapi.query import ApiQueryParams, api_query_params_dep
from demo_bd.schemas.app_info import InfoResponseSchema, StatusCheckResponseSchema
from demo_bd.utils.formatters.datetime_formatter import fmt_datetime_into_iso8601_format

start_time = pendulum.now()

UNAUTHORIZED_401_RESPONSE = {
    "description": "Unauthorized - Invalid or missing API key",
    "content": {
        "application/json": {
            "example": {
                "type": "about:blank",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Invalid or missing API key",
            }
        }
    },
}

health_info_route = APIRouter(prefix="/v1/health", tags=["health"])


@health_info_route.get(
    "/status",
    name="health:status",
    summary="Check API health status",
    description=(
        "Returns a simple message indicating that the API is running and accessible.\n\n"
        "### Usage\n"
        "- Can be used for health checks and monitoring.\n"
        "- Requires a valid API key for authentication.\n\n"
        "#### Response\n"
        "A JSON object with a welcome message."
    ),
    response_description="A message confirming the API is up and running.",
    status_code=status.HTTP_200_OK,
    responses={200: {"description": "API is healthy"}, 401: UNAUTHORIZED_401_RESPONSE},
)
def status_check(
    query: ApiQueryParams = api_query_params_dep,
    api_key: str = Depends(
        make_api_key_dependency(
            apikey_name=settings.SECURITY.APIKEY_NAME,
            apikey_value=settings.SECURITY.APIKEY,
        )
    ),
) -> StatusCheckResponseSchema:
    """Health status check endpoint. Returns a welcome message indicating the API is up."""
    return StatusCheckResponseSchema(message=f"Hello, Welcome to {settings.APP_TITLE} Status API!")


@health_info_route.get(
    "/info",
    name="health:info",
    summary="Get application information",
    description=(
        "Returns detailed information about the application, including name, version, current timestamp, uptime, and environment.\n\n"
        "### Usage\n"
        "- Useful for diagnostics and monitoring.\n"
        "- Requires a valid API key for authentication.\n\n"
        "#### Response\n"
        "A JSON object with application metadata."
    ),
    response_description="Application metadata including name, version, timestamp, uptime, and environment.",
    status_code=status.HTTP_200_OK,
    responses={200: {"description": "Application information"}, 401: UNAUTHORIZED_401_RESPONSE},
)
def info(
    query: ApiQueryParams = api_query_params_dep,
    api_key: str = Depends(
        make_api_key_dependency(
            apikey_name=settings.SECURITY.APIKEY_NAME,
            apikey_value=settings.SECURITY.APIKEY,
        )
    ),
) -> InfoResponseSchema:
    """Return application information including name, version, timestamp, uptime, and environment."""
    uptime = round((pendulum.now() - start_time).total_seconds(), 2)
    return InfoResponseSchema(
        app_name=settings.APP_SLUG,
        app_title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        timestamp=fmt_datetime_into_iso8601_format(pendulum.now()),
        uptime_seconds=uptime,
        environment=settings.env,
    )


@health_info_route.get("/custom_error_test")
def custom_error_test() -> dict:
    """Raise a sample ProblemException for testing error responses."""
    raise ProblemException(
        status=status.HTTP_400_BAD_REQUEST,
        detail="This was a bad request to the API.",
        service_1="down",
        service_2="up",
        matadata={"key": "value"},
        headers={"Retry-After": "30"},
    )
