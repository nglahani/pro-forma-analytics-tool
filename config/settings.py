"""
Global Settings and Configuration

Manages application-wide settings including forecast horizons,
database connections, API configurations, and update schedules.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import os
import json

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
    percentiles: List[float] = None
    
    def __post_init__(self):
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
    """API configuration settings."""
    fred_api_key: str = ""
    fred_base_url: str = "https://api.stlouisfed.org/fred"
    rate_limit_requests_per_minute: int = 120
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cache_duration_hours: int = 24
    
    def __post_init__(self):
        # Try to load API key from multiple sources (priority order)
        # 1. Environment variable (highest priority)
        self.fred_api_key = os.getenv("FRED_API_KEY", self.fred_api_key)
        
        # 2. Configuration file (if environment variable not set)
        if not self.fred_api_key:
            try:
                config_path = Path(__file__).parent / "api_keys.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        self.fred_api_key = config.get("fred_api_key", "")
            except Exception as e:
                # Fail silently and use empty key (will be handled by collectors)
                pass

@dataclass
class UpdateSchedule:
    """Data update schedule configuration."""
    monthly_parameters: List[str] = None
    quarterly_parameters: List[str] = None
    annual_parameters: List[str] = None
    auto_update_enabled: bool = True
    update_time_hour: int = 2  # 2 AM local time
    
    def __post_init__(self):
        if self.monthly_parameters is None:
            self.monthly_parameters = [
                "treasury_10y", 
                "commercial_mortgage_rate",
                "cpi_housing"
            ]
        if self.quarterly_parameters is None:
            self.quarterly_parameters = [
                "rental_vacancy_rate",
                "multifamily_cap_rate", 
                "house_price_index"
            ]
        if self.annual_parameters is None:
            self.annual_parameters = [
                "rent_growth_msa",
                "property_tax_growth"
            ]

class Settings:
    """Main settings manager."""
    
    def __init__(self):
        self.forecast = ForecastSettings()
        self.monte_carlo = MonteCarloSettings()
        self.database = DatabaseSettings()
        self.api = APISettings()
        self.updates = UpdateSchedule()
        self.project_root = Path(__file__).parent.parent
        
    def validate_forecast_horizon(self, years: int) -> bool:
        """Validate forecast horizon is within allowed range."""
        return (self.forecast.min_horizon_years <= years <= 
                self.forecast.max_horizon_years)
    
    def get_data_path(self, *path_parts) -> Path:
        """Get path relative to project data directory."""
        return self.project_root / "data" / Path(*path_parts)
    
    def get_cache_path(self, *path_parts) -> Path:
        """Get path relative to cache directory."""
        return self.project_root / "data" / "cache" / Path(*path_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for serialization."""
        return {
            "forecast": {
                "min_horizon_years": self.forecast.min_horizon_years,
                "max_horizon_years": self.forecast.max_horizon_years,
                "default_horizon_years": self.forecast.default_horizon_years,
                "confidence_intervals": self.forecast.confidence_intervals
            },
            "monte_carlo": {
                "default_num_simulations": self.monte_carlo.default_num_simulations,
                "correlation_window_years": self.monte_carlo.correlation_window_years,
                "percentiles": self.monte_carlo.percentiles
            },
            "database": {
                "base_path": self.database.base_path,
                "backup_frequency_days": self.database.backup_frequency_days
            },
            "api": {
                "rate_limit_requests_per_minute": self.api.rate_limit_requests_per_minute,
                "timeout_seconds": self.api.timeout_seconds,
                "cache_duration_hours": self.api.cache_duration_hours
            }
        }

# Global settings instance
settings = Settings()

# Validation functions
def validate_api_key(api_key: str) -> bool:
    """Validate FRED API key format."""
    return len(api_key) == 32 and api_key.isalnum()

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        settings.get_data_path("databases"),
        settings.get_data_path("api_sources"), 
        settings.get_cache_path(),
        settings.project_root / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    "monte_carlo_simulations": 1000,  # Faster for testing
    "api_rate_limit": 60,  # More conservative
    "cache_duration_hours": 1  # Shorter cache for testing
}

PRODUCTION_CONFIG = {
    "monte_carlo_simulations": 10000,
    "api_rate_limit": 120,
    "cache_duration_hours": 24
}

def apply_config(config_name: str = "development"):
    """Apply environment-specific configuration."""
    config = DEVELOPMENT_CONFIG if config_name == "development" else PRODUCTION_CONFIG
    
    settings.monte_carlo.default_num_simulations = config["monte_carlo_simulations"]
    settings.api.rate_limit_requests_per_minute = config["api_rate_limit"] 
    settings.api.cache_duration_hours = config["cache_duration_hours"]