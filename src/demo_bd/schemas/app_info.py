"""Schema definitions for application information responses."""

from typing import ClassVar

from demo_bd.schemas.base import BaseSchemaModel


class InfoResponseSchema(BaseSchemaModel):
    """Schema for application information response."""

    app_name: str
    app_title: str
    version: str
    timestamp: str
    uptime_seconds: float
    environment: str

    class Config:
        """Pydantic configuration for example schema."""

        json_schema_extra: ClassVar[dict] = {
            "example": {
                "app_name": "demo-bd",
                "app_title": "Demo BD",
                "version": "1.0.0",
                "timestamp": "2025-05-19T17:20:00Z",
                "uptime_seconds": 12345.67,
                "environment": "production",
            }
        }


class StatusCheckResponseSchema(BaseSchemaModel):
    """Schema for health status check response."""

    message: str

    class Config:
        """Pydantic configuration for example schema."""

        json_schema_extra: ClassVar[dict] = {
            "example": {"message": "Hello, Welcome to Demo BD Status API!"}
        }
