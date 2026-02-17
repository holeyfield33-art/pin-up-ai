"""Application configuration via environment variables."""

import os
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    # App
    app_name: str = Field(default="Pin-Up AI", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )

    # Database -- PINUP_DB is canonical (set by Tauri sidecar)
    pinup_db: str = Field(default="pinup.db", alias="PINUP_DB")
    database_check_same_thread: bool = Field(default=False, alias="DB_CHECK_SAME_THREAD")

    # Server
    pinup_port: int = Field(default=8000, alias="PINUP_PORT")
    host: str = Field(default="127.0.0.1", alias="PINUP_HOST")

    # Logging
    pinup_log_level: str = Field(default="INFO", alias="PINUP_LOG_LEVEL")
    log_format: Literal["json", "text"] = Field(default="json", alias="LOG_FORMAT")

    # CORS -- allow Tauri webview + local dev
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "tauri://localhost",
            "https://tauri.localhost",
        ],
        alias="CORS_ORIGINS",
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=200, alias="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, alias="RATE_LIMIT_PERIOD")

    # Export
    max_export_size: int = Field(default=50_000_000, alias="MAX_EXPORT_SIZE")

    # Backup
    backup_dir: str = Field(default="", alias="PINUP_BACKUP_DIR")

    # Trial
    trial_days: int = Field(default=14, alias="PINUP_TRIAL_DAYS")

    # Gumroad (set to enable server-side license validation)
    gumroad_product_id: str = Field(default="", alias="PINUP_GUMROAD_PRODUCT_ID")

    def get_database_path(self) -> str:
        """Return absolute path to SQLite DB file."""
        p = self.pinup_db
        if os.path.isabs(p):
            return p
        return os.path.abspath(p)

    def get_database_url(self) -> str:
        """SQLAlchemy URL for the SQLite DB."""
        abspath = self.get_database_path()
        return f"sqlite:///{abspath}"

    def get_backup_dir(self) -> str:
        """Return absolute path to backups directory."""
        if self.backup_dir:
            return os.path.abspath(self.backup_dir)
        db_dir = os.path.dirname(self.get_database_path())
        return os.path.join(db_dir, "backups")


settings = Settings()
