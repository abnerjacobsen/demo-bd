"""Snap FastStream Template settings."""

# BUILTIN modules
from functools import lru_cache

# Third party modules
from pydantic_settings import SettingsConfigDict

# SnapEnv base modules
from snap_core.config.manager import (
    SnapEnvCommonSettings,
)


class AppSettings(SnapEnvCommonSettings):
    """
    Application settings configuration.

    Attributes
    ----------
    APP_TITLE : str
        The title of the application.
    LOG_LEVEL : str
        The log level for the application.
    model_config : SettingsConfigDict
        Configuration dictionary for environment settings, initialized with the environment file.
    """

    APP_TITLE: str
    LOG_LEVEL: str

    model_config = SettingsConfigDict(env_file=f"{SnapEnvCommonSettings().env}.env")


@lru_cache
def get_settings() -> AppSettings:
    """
    Retrieve the application settings with caching.

    This function uses an LRU cache to store the settings so that
    subsequent calls are fast and do not re-initialize the settings.

    Returns
    -------
    AppSettings
        The application settings instance.
    """
    return AppSettings()


settings: AppSettings = get_settings()
