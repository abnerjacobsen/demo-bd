"""API key authentication utilities for FastAPI routes.

Provides dependencies and helpers for extracting and validating API keys
from headers, query parameters, or cookies, using project settings.
"""

from collections.abc import Callable

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKeyQuery


def make_api_key_dependency(
    apikey_name: str,
    apikey_value: str,
) -> Callable:
    """Create an API key dependency for FastAPI routes.

    Args:
        apikey_name (str): The name of the API key (header, query, or cookie).
        apikey_value (str): The expected value of the API key.

    Returns
    -------
        Callable: A dependency callable for FastAPI that validates the API key.
    """
    api_key_header = APIKeyHeader(name=apikey_name, auto_error=False)
    api_key_query = APIKeyQuery(name=apikey_name, auto_error=False)
    api_key_cookie = APIKeyCookie(name=apikey_name, auto_error=False)

    async def get_api_key(
        api_key_header_data: str = Security(api_key_header),
        api_key_query_data: str = Security(api_key_query),
        api_key_cookie_data: str = Security(api_key_cookie),
    ):
        """
        Retrieve the API key from the request header, query parameter, or cookie.

        Args:
            api_key_header_data (str): API key provided in the request header.
            api_key_query_data (str): API key provided in the query parameter.
            api_key_cookie_data (str): API key provided in the cookie.

        Raises
        ------
            HTTPException: If the API key is missing or invalid.

        Returns
        -------
            str: The validated API key.
        """
        if api_key_header_data == apikey_value:
            return api_key_header_data
        if api_key_query_data == apikey_value:
            return api_key_query_data
        if api_key_cookie_data == apikey_value:
            return api_key_cookie_data
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return get_api_key
