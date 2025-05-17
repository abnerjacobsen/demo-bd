"""Database manager and SQLAlchemy configuration for demo_bd."""

from sqlalchemy_bind_manager import SQLAlchemyBindManager, SQLAlchemyConfig

from demo_bd.core.config.settings import settings

bind_config = {
    "default": SQLAlchemyConfig(
        engine_url=settings.DB.dsn,
        # engine_options=dict(connect_args={"check_same_thread": False}, echo=True),
        engine_options={
            "connect_args": {
                "server_settings": {
                    "application_name": f"{settings.TENANT_SLUG}_{settings.APP_SLUG}"
                },
                "check_same_thread": False,
            },
            "echo": settings.DB.DB_ECHO_DEBUG,
        },
        session_options={"expire_on_commit": False},
        async_engine=True,
    ),
}


sa_manager = SQLAlchemyBindManager(config=bind_config)
