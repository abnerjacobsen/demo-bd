import pendulum
from fastapi import APIRouter, Depends, Request, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_problem_details import ProblemException

from demo_bd.core.config.settings import settings
from demo_bd.core.fastapi.apikey import make_api_key_dependency
from demo_bd.schemas.base import BaseSchemaModel
from demo_bd.utils.formatters.datetime_formatter import fmt_datetime_into_iso8601_format

start_time = pendulum.now()


async def check_auth(
    request: Request,
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> bool:
    if authorization is None:
        raise ProblemException(
            status=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            service_1="down",
            service_2="up",
            service_3={"a": "b"},
            headers={"Retry-After": "30"},
        )

    if authorization.credentials != "permitted":
        msg = "No active permissions."
        raise ProblemException(
            status=status.HTTP_403_FORBIDDEN,
            detail=msg,
        )

    return True


health_info_route = APIRouter(prefix="/v1/health", tags=["healt"])


@health_info_route.get(
    "/status",
    name="health:status",
    summary="Health status check.",
    status_code=status.HTTP_200_OK,
)
def status_check(
    api_key: str = Depends(
        make_api_key_dependency(
            apikey_name=settings.SECURITY.APIKEY_NAME,
            apikey_value=settings.SECURITY.APIKEY,
        )
    ),
) -> dict:
    return {"message": f"Hello, Welcome to {settings.APP_TITLE} Status API!"}


@health_info_route.get("/authorized")
async def authorized(
    authorized=Depends(check_auth),
) -> dict:
    return {"authorized": authorized}


class User(BaseSchemaModel):
    id: str
    name: str


@health_info_route.post("/users/")
def create_user(_user: User) -> User:
    return _user


@health_info_route.get("/info")
def info() -> dict:
    uptime = round((pendulum.now() - start_time).total_seconds(), 2)
    return {
        "app_name": settings.APP_SLUG,
        "app_title": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "timestamp": fmt_datetime_into_iso8601_format(pendulum.now()),
        "uptime_seconds": uptime,
        "environment": settings.env,
    }


class TestUnhandledError:
    class FakeError(Exception):
        pass


@health_info_route.get("/info_error_500")
def info_error_500() -> dict:
    raise TestUnhandledError.FakeError("erro 500, eu espero")
