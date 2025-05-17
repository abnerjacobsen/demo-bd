"""
Configurações centrais do Demo BD.

Este módulo centraliza e organiza todas as configurações essenciais da aplicação Demo BD,
incluindo parâmetros de conexão com o banco de dados PostgreSQL, metadados da aplicação,
controle de ambiente, plataforma, logging e integração multi-tenant.

Principais componentes:

- DbSettings: configurações detalhadas para conexão e autenticação com o banco de dados, com montagem automática da string de conexão (DSN).
- AppSettings: configurações globais da aplicação, incluindo ambiente, plataforma, metadados, logging e referência às configurações de banco de dados.
- get_settings: função utilitária com cache para obter as configurações já validadas, evitando reprocessamento e garantindo performance.

As configurações são baseadas em Pydantic e SnapEnv, permitindo validação automática, tipagem forte e fácil extensão para múltiplos ambientes (desenvolvimento, produção, etc).

Uso típico:
-----------
    from demo_bd.core.config.settings import settings
    db_url = settings.DB.dsn

"""

# BUILTIN modules
import platform
import sys
from functools import lru_cache

from pydantic import computed_field

# SnapEnv base modules
from snapenv_core.settings.manager import ENVIRONMENT, PLATFORM, SnapEnvCommonSettings


class DbSettings(SnapEnvCommonSettings):
    """
    Database connection and configuration settings.

    This class centralizes all configuration options required to connect to the application's PostgreSQL database,
    including credentials, host, port, driver, and debug options.

    Attributes
    ----------
    POSTGRES_HOST : str
        Hostname or IP address of the PostgreSQL server.
    POSTGRES_PORT : int
        Port number on which the PostgreSQL server is listening.
    POSTGRES_DB : str
        Name of the PostgreSQL database to connect to.
    POSTGRES_USER : str
        Username for authenticating with the PostgreSQL database.
    POSTGRES_PASSWORD : str
        Password for authenticating with the PostgreSQL database.
    POSTGRES_DRIVER : str
        SQLAlchemy driver string for PostgreSQL connections (default: "postgresql+asyncpg").
    DB_ECHO_DEBUG : bool
        If True, enables SQLAlchemy debug logging (echo SQL statements).
    dsn : str
        Computed property. Returns the full database connection string (DSN) assembled from the above fields.

    Notes
    -----
    Inherits from SnapEnvCommonSettings, which provides base environment configuration.
    """

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DRIVER: str = "postgresql+asyncpg"
    DB_ECHO_DEBUG: bool

    # Computed settings
    @computed_field  # type: ignore[misc]
    @property
    def dsn(self) -> str:
        """
        Assemble and return the PostgreSQL DSN (connection string) using the configured driver, credentials, host, port, and database.

        Returns
        -------
        str
            The generated connection URL (DSN).
        """
        return f"{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class AppSettings(SnapEnvCommonSettings):
    """
    Main application settings.

    This class centralizes all configuration options for the Demo BD application,
    including environment, platform, application metadata, logging, and database settings.

    Attributes
    ----------
    env : str
        The current environment (e.g., "development", "production").
    platform : str
        The current platform identifier (e.g., "linux", "windows", "other").
    APP_TITLE : str
        The title of the application.
    APP_SLUG : str
        The slug identifier for the application.
    TENANT_SLUG : str
        The tenant slug for multi-tenant deployments.
    LOG_LEVEL : str
        The log level for the application (e.g., "INFO", "DEBUG").
    DEBUG : bool
        Activate debug.
    DB : DbSettings
        Database configuration settings (instance of DbSettings).
    server : str
        Computed property. Returns the local server name (hostname) in upper case, stripped of any domain part.

    Notes
    -----
    Inherits from SnapEnvCommonSettings, which provides base environment configuration.
    """

    # Environment depending settings
    env: str = ENVIRONMENT
    platform: str = PLATFORM.get(sys.platform, "other")

    # App settings
    APP_TITLE: str
    APP_SLUG: str
    TENANT_SLUG: str
    LOG_LEVEL: str
    DEBUG: bool
    DB: DbSettings = DbSettings()

    # Computed settings
    @computed_field  # type: ignore[misc]
    @property
    def server(self) -> str:
        """
        Return local server name stripped of possible domain part.

        Returns
        -------
        str
            Server name in upper case.
        """
        return platform.node()


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
