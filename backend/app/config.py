"""Application configuration via environment variables."""

from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # App settings
    app_name: str = Field(default="Pin-Up AI", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./pinup.db",
        alias="DATABASE_URL",
        description="SQLite database path or connection string",
    )
    database_check_same_thread: bool = Field(
        default=False, alias="DB_CHECK_SAME_THREAD"
    )

    # API
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    api_title: str = Field(default="Pin-Up AI API", alias="API_TITLE")
    api_docs_url: str = Field(default="/docs", alias="API_DOCS_URL")
    api_redoc_url: str = Field(default="/redoc", alias="API_REDOC_URL")

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "tauri://localhost",
        ],
        alias="CORS_ORIGINS",
    )
    cors_credentials: bool = Field(default=True, alias="CORS_CREDENTIALS")
    cors_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        alias="CORS_METHODS",
    )
    cors_headers: list[str] = Field(
        default_factory=lambda: ["*"],
        alias="CORS_HEADERS",
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, alias="RATE_LIMIT_PERIOD")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: Literal["json", "text"] = Field(
        default="json", alias="LOG_FORMAT"
    )

    # Export
    max_export_size: int = Field(default=10_000_000, alias="MAX_EXPORT_SIZE")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_database_url(self) -> str:
        """Get database URL for SQLite with WAL mode."""
        url = self.database_url
        if url.startswith("sqlite"):
            return url
        return url


settings = Settings()
