"""
Environment Configuration Management

Enhanced configuration system supporting multiple environments (dev/test/prod).
Handles environment variables, secrets, API settings, and application configuration.
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.exceptions import ConfigurationError


class Environment(Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class ForecastSettings:
    """Settings for Prophet forecasting."""

    min_horizon_years: int = 3
    max_horizon_years: int = 10
    default_horizon_years: int = 5
    confidence_interval: float = 0.95  # 95% confidence interval
    yearly_seasonality: bool = True
    weekly_seasonality: bool = False
    daily_seasonality: bool = False
    changepoint_prior_scale: float = 0.05  # Flexibility of trend changes
    seasonality_prior_scale: float = 10.0  # Flexibility of seasonality
    uncertainty_samples: int = 1000  # Samples for uncertainty estimation


@dataclass
class MonteCarloSettings:
    """Settings for Monte Carlo simulation."""

    default_num_simulations: int = 10000
    correlation_window_years: int = 5
    seed: int = 42
    percentiles: Optional[List[float]] = None

    def __post_init__(self) -> None:
        if self.percentiles is None:
            self.percentiles = [5, 10, 25, 50, 75, 90, 95]


@dataclass
class DatabaseSettings:
    """Database configuration settings."""

    base_path: str = "data/databases"
    market_data_db: str = "market_data.db"
    property_data_db: str = "property_data.db"
    economic_data_db: str = "economic_data.db"
    forecast_cache_db: str = "forecast_cache.db"
    backup_frequency_days: int = 7

    def get_db_path(self, db_name: str) -> Path:
        """Get full path to a database file."""
        return Path(self.base_path) / db_name


@dataclass
class APISettings:
    """Web API server configuration."""

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1

    # Security
    secret_key: str = ""
    api_key_header: str = "X-API-Key"
    allowed_origins: Optional[List[str]] = None

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    def __post_init__(self) -> None:
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]  # Default allow all for development


@dataclass
class ExternalAPISettings:
    """External API configuration settings."""

    fred_api_key: str = ""
    fred_base_url: str = "https://api.stlouisfed.org/fred"
    rate_limit_requests_per_minute: int = 120
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cache_duration_hours: int = 24

    def __post_init__(self) -> None:
        # Load API key from environment variable ONLY
        self.fred_api_key = os.getenv("FRED_API_KEY", "")


@dataclass
class UpdateSchedule:
    """Data update schedule configuration."""

    monthly_parameters: Optional[List[str]] = None
    quarterly_parameters: Optional[List[str]] = None
    annual_parameters: Optional[List[str]] = None
    auto_update_enabled: bool = True
    update_time_hour: int = 2  # 2 AM local time

    def __post_init__(self) -> None:
        if self.monthly_parameters is None:
            self.monthly_parameters = [
                "treasury_10y",
                "commercial_mortgage_rate",
                "cpi_housing",
            ]
        if self.quarterly_parameters is None:
            self.quarterly_parameters = [
                "rental_vacancy_rate",
                "multifamily_cap_rate",
                "house_price_index",
            ]
        if self.annual_parameters is None:
            self.annual_parameters = ["rent_growth_msa", "property_tax_growth"]


class Settings:
    """
    Enhanced settings manager with environment-based configuration.

    Supports multiple environments: development, testing, production.
    Loads configuration from environment variables with sensible defaults.
    """

    def __init__(self) -> None:
        self.environment = self._get_environment()
        self.project_root = Path(__file__).parent.parent

        # Load configuration based on environment
        self.forecast = ForecastSettings()
        self.monte_carlo = MonteCarloSettings()
        self.database = self._load_database_settings()
        self.api = self._load_api_settings()
        self.external_apis = ExternalAPISettings()
        self.updates = UpdateSchedule()

        # Validate critical settings
        self._validate_configuration()

    def _get_environment(self) -> Environment:
        """Determine current environment."""
        env_name = os.getenv("PRO_FORMA_ENV", "development").lower()
        try:
            return Environment(env_name)
        except ValueError:
            raise ConfigurationError(
                f"Invalid environment: {env_name}. Must be one of: {[e.value for e in Environment]}"
            )

    def _load_database_settings(self) -> DatabaseSettings:
        """Load database settings based on environment."""
        settings = DatabaseSettings()

        if self.environment == Environment.TESTING:
            # Use separate test databases
            settings.base_path = "data/databases/test"
        elif self.environment == Environment.PRODUCTION:
            # Use production database path
            settings.base_path = os.getenv("DB_BASE_PATH", "data/databases/prod")
            settings.backup_frequency_days = int(os.getenv("DB_BACKUP_FREQUENCY", "1"))

        return settings

    def _load_api_settings(self) -> APISettings:
        """Load API settings based on environment."""
        settings = APISettings(
            host=os.getenv("API_HOST", "127.0.0.1"),
            port=int(os.getenv("API_PORT", "8000")),
            debug=self.environment == Environment.DEVELOPMENT,
            reload=self.environment == Environment.DEVELOPMENT,
            workers=int(os.getenv("API_WORKERS", "1")),
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
            api_key_header=os.getenv("API_KEY_HEADER", "X-API-Key"),
            rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
        )

        # Parse allowed origins
        origins_str = os.getenv("ALLOWED_ORIGINS", "*")
        if origins_str == "*":
            settings.allowed_origins = ["*"]
        else:
            settings.allowed_origins = [
                origin.strip() for origin in origins_str.split(",")
            ]

        return settings

    def _validate_configuration(self) -> None:
        """Validate critical configuration settings."""
        errors = []

        # Validate external API keys in production
        if self.environment == Environment.PRODUCTION:
            if not self.external_apis.fred_api_key:
                errors.append(
                    "FRED_API_KEY environment variable is required in production"
                )

            if self.api.secret_key == "dev-secret-key-change-in-production":
                errors.append(
                    "SECRET_KEY environment variable must be set in production"
                )

        if errors:
            raise ConfigurationError(
                f"Configuration validation failed: {'; '.join(errors)}"
            )

    def validate_forecast_horizon(self, years: int) -> bool:
        """Validate forecast horizon is within allowed range."""
        return (
            self.forecast.min_horizon_years <= years <= self.forecast.max_horizon_years
        )

    def get_data_path(self, *path_parts: str) -> Path:
        """Get path relative to project data directory."""
        return self.project_root / "data" / Path(*path_parts)

    def get_cache_path(self, *path_parts: str) -> Path:
        """Get path relative to cache directory."""
        return self.project_root / "data" / "cache" / Path(*path_parts)

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)."""
        return {
            "environment": self.environment.value,
            "forecast": {
                "min_horizon_years": self.forecast.min_horizon_years,
                "max_horizon_years": self.forecast.max_horizon_years,
                "default_horizon_years": self.forecast.default_horizon_years,
                "confidence_interval": self.forecast.confidence_interval,
            },
            "monte_carlo": {
                "default_num_simulations": self.monte_carlo.default_num_simulations,
                "correlation_window_years": self.monte_carlo.correlation_window_years,
                "percentiles": self.monte_carlo.percentiles,
            },
            "database": {
                "base_path": self.database.base_path,
                "backup_frequency_days": self.database.backup_frequency_days,
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "debug": self.api.debug,
                "allowed_origins": self.api.allowed_origins,
                "rate_limit_requests": self.api.rate_limit_requests,
            },
            "external_apis": {
                "fred_base_url": self.external_apis.fred_base_url,
                "rate_limit_requests_per_minute": self.external_apis.rate_limit_requests_per_minute,
                "timeout_seconds": self.external_apis.timeout_seconds,
                "cache_duration_hours": self.external_apis.cache_duration_hours,
            },
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def reload_settings() -> Settings:
    """Reload settings (useful for testing)."""
    global settings
    settings = Settings()
    return settings


# Validation functions
def validate_api_key(api_key: str) -> bool:
    """Validate FRED API key format."""
    return len(api_key) == 32 and api_key.isalnum()


def create_directories() -> None:
    """Create necessary directories if they don't exist."""
    directories = [
        settings.get_data_path("databases"),
        settings.get_data_path("api_sources"),
        settings.get_cache_path(),
        settings.project_root / "logs",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "monte_carlo_simulations": 1000,  # Faster for testing
    "api_rate_limit": 60,  # More conservative
    "cache_duration_hours": 1,  # Shorter cache for testing
}

PRODUCTION_CONFIG = {
    "monte_carlo_simulations": 10000,
    "api_rate_limit": 120,
    "cache_duration_hours": 24,
}


def apply_config(config_name: str = "development") -> None:
    """Apply environment-specific configuration."""
    config = DEVELOPMENT_CONFIG if config_name == "development" else PRODUCTION_CONFIG

    # Apply known, valid settings
    settings.monte_carlo.default_num_simulations = config["monte_carlo_simulations"]
    # Map to existing APISettings fields
    settings.api.rate_limit_requests = config["api_rate_limit"]
    # Note: cache configuration is managed per-service; no direct APISettings field
