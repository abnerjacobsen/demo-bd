"""Fastapi security APIKEY."""

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery

from demo_bd.core.config.settings import settings

api_key_header = APIKeyHeader(name=settings.SECURITY.APIKEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name=settings.SECURITY.APIKEY_NAME, auto_error=False)
# api_key_cookie = APIKeyCookie(name=settings.DAS_APIKEY_NAME, auto_error=False)


async def get_api_key(
    api_key_header_data: str = Security(api_key_header),
    api_key_query_data: str = Security(api_key_query),
    # api_key_cookie_data: str = Security(api_key_cookie),
):
    """
    Retrieve the API key from the request header or query parameter.

    Args:
        api_key_header_data (str): API key provided in the request header.
        api_key_query_data (str): API key provided in the query parameter.

    Raises
    ------
        HTTPException: If the API key is missing or invalid.

    Returns
    -------
        str: The validated API key.
    """
    if api_key_header_data == settings.SECURITY.APIKEY:
        return api_key_header_data
    elif api_key_query_data == settings.SECURITY.APIKEY:  # noqa: RET505
        return api_key_query_data
    # elif api_key_cookie_data == settings.SECURITY.APIKEY:
    #     return api_key_cookie_data
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
