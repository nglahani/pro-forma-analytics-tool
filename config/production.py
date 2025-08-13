"""
Production Configuration for Pro-Forma Analytics Tool

This module contains production-specific configuration settings.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, validator
from pydantic_settings import SettingsConfigDict


class ProductionSettings(BaseSettings):
    """Production environment settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Environment
    environment: str = "production"
    debug: bool = False

    # API Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Security
    secret_key: str
    api_key_header: str = "X-API-Key"
    allowed_origins: list[str] = ["https://proforma.example.com"]

    # Database Configuration
    database_url: Optional[str] = None
    db_base_path: str = "data/databases"
    db_backup_frequency: int = 7
    db_pool_size: int = 20
    db_max_overflow: int = 0
    db_pool_timeout: int = 30
    db_pool_recycle: int = -1

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20
    redis_socket_keepalive: bool = True
    redis_socket_keepalive_options: dict = {
        "TCP_KEEPIDLE": 1,
        "TCP_KEEPINTVL": 3,
        "TCP_KEEPCNT": 5,
    }

    # Rate Limiting
    rate_limit_requests: int = 1000
    rate_limit_window: int = 60
    rate_limit_storage: str = "redis://localhost:6379/1"

    # Caching
    cache_enabled: bool = True
    cache_backend: str = "redis"
    cache_ttl_seconds: int = 3600
    cache_max_entries: int = 10000

    # External APIs
    fred_api_key: Optional[str] = None
    fred_api_base_url: str = "https://api.stlouisfed.org/fred"
    fred_request_timeout: int = 30
    fred_max_retries: int = 3

    # Logging Configuration
    log_level: str = "INFO"
    log_file_path: str = "logs/proforma.log"
    log_max_file_size_mb: int = 100
    log_backup_count: int = 10
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_json_format: bool = True

    # Monitoring and Metrics
    prometheus_enabled: bool = True
    prometheus_port: int = 8001
    metrics_path: str = "/api/v1/metrics"
    health_check_interval: int = 30

    # Sentry Configuration
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "production"
    sentry_traces_sample_rate: float = 0.1

    # Performance Settings
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 300  # 5 minutes
    worker_timeout: int = 300
    keep_alive: int = 2

    # Monte Carlo Configuration
    monte_carlo_max_scenarios: int = 50000
    monte_carlo_default_scenarios: int = 1000
    monte_carlo_timeout: int = 300
    monte_carlo_batch_size: int = 1000

    # DCF Analysis Configuration
    dcf_analysis_timeout: int = 60
    dcf_max_concurrent: int = 10
    dcf_default_discount_rate: float = 0.10

    # Security Headers
    security_headers: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    # CORS Settings
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-API-Key",
    ]
    cors_max_age: int = 86400

    # Backup Configuration
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days: int = 30
    s3_backup_bucket: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # SSL/TLS Configuration
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_certs: Optional[str] = None

    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validate SECRET_KEY is sufficiently strong for production."""
        if not v:
            raise ValueError("SECRET_KEY is required for production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @validator("allowed_origins")
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins if provided as string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("database_url")
    def validate_database_url(cls, v, values):
        """Set default database URL if not provided."""
        if not v:
            db_base_path = values.get("db_base_path", "data/databases")
            return f"sqlite:///{db_base_path}/proforma_production.db"
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @validator("sentry_traces_sample_rate")
    def validate_sentry_sample_rate(cls, v):
        """Validate Sentry sample rate."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Sentry traces sample rate must be between 0.0 and 1.0")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def database_config(self) -> dict:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
            "pool_recycle": self.db_pool_recycle,
        }

    @property
    def redis_config(self) -> dict:
        """Get Redis configuration dictionary."""
        return {
            "url": self.redis_url,
            "max_connections": self.redis_max_connections,
            "socket_keepalive": self.redis_socket_keepalive,
            "socket_keepalive_options": self.redis_socket_keepalive_options,
        }

    @property
    def logging_config(self) -> dict:
        """Get logging configuration dictionary."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": self.log_format,
                    "class": (
                        "pythonjsonlogger.jsonlogger.JsonFormatter"
                        if self.log_json_format
                        else None
                    ),
                },
                "simple": {
                    "format": "%(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "level": self.log_level,
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                },
                "file": {
                    "level": self.log_level,
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": self.log_file_path,
                    "maxBytes": self.log_max_file_size_mb * 1024 * 1024,
                    "backupCount": self.log_backup_count,
                    "formatter": "detailed",
                },
            },
            "loggers": {
                "": {
                    "level": self.log_level,
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
                "fastapi": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False,
                },
            },
        }

    @property
    def uvicorn_config(self) -> dict:
        """Get Uvicorn server configuration."""
        return {
            "host": self.api_host,
            "port": self.api_port,
            "workers": self.api_workers,
            "log_level": self.log_level.lower(),
            "access_log": True,
            "use_colors": False,
            "timeout_keep_alive": self.keep_alive,
            "limit_max_requests": 10000,
            "limit_concurrency": 1000,
        }

    def create_directories(self) -> None:
        """Create necessary directories for production."""
        directories = [
            Path(self.db_base_path),
            Path(self.log_file_path).parent,
            Path("backups"),
            Path("cache"),
            Path("monitoring/data"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def validate_production_requirements(self) -> list[str]:
        """Validate production requirements and return any issues."""
        issues = []

        # Check required environment variables
        if not self.secret_key or len(self.secret_key) < 32:
            issues.append("SECRET_KEY must be at least 32 characters")

        if not self.fred_api_key and os.getenv("FRED_API_KEY"):
            issues.append("FRED_API_KEY is recommended for market data")

        # Check SSL configuration in production
        if self.is_production:
            if not self.ssl_cert_path or not self.ssl_key_path:
                issues.append(
                    "SSL certificates (ssl_cert_path, ssl_key_path) are recommended for production"
                )

        # Check Sentry configuration
        if not self.sentry_dsn:
            issues.append("SENTRY_DSN is recommended for error tracking in production")

        # Check backup configuration
        if self.backup_enabled and not (
            self.s3_backup_bucket and self.aws_access_key_id
        ):
            issues.append(
                "AWS S3 configuration required for backups (S3_BACKUP_BUCKET, AWS_ACCESS_KEY_ID)"
            )

        return issues


# Create global settings instance
def get_production_settings() -> ProductionSettings:
    """Get production settings instance."""
    return ProductionSettings()


# Export commonly used configurations
def get_database_url() -> str:
    """Get production database URL."""
    settings = get_production_settings()
    return settings.database_url


def get_redis_url() -> str:
    """Get production Redis URL."""
    settings = get_production_settings()
    return settings.redis_url


def is_sentry_enabled() -> bool:
    """Check if Sentry error tracking is enabled."""
    settings = get_production_settings()
    return bool(settings.sentry_dsn)
