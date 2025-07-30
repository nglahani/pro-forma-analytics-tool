"""
Cached Parameter Repository

Provides a caching layer over the SQLite parameter repository
for improved performance on frequently accessed data.
"""

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.domain.entities.forecast import ForecastResult, HistoricalData, ParameterId
from src.infrastructure.cache.query_cache import cached_query, get_query_cache
from src.infrastructure.repositories.sqlite_parameter_repository import (
    SQLiteCorrelationRepository,
    SQLiteForecastRepository,
    SQLiteParameterRepository,
)


class CachedParameterRepository:
    """Parameter repository with intelligent caching for performance optimization."""

    def __init__(self, db_path: str):
        self.repository = SQLiteParameterRepository(db_path)
        self.cache = get_query_cache()

    def save_historical_data(self, historical_data: HistoricalData) -> None:
        """Save historical data and invalidate related cache entries."""
        # Clear cache entries related to this parameter
        cache_pattern = f"%{historical_data.parameter_id.name}%{historical_data.parameter_id.geographic_code}%"
        self.cache.invalidate(cache_pattern)

        return self.repository.save_historical_data(historical_data)

    @cached_query(ttl_seconds=3600)  # Cache for 1 hour
    def get_historical_data(
        self,
        parameter_id: ParameterId,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[HistoricalData]:
        """Get historical data with caching."""
        return self.repository.get_historical_data(parameter_id, start_date, end_date)

    @cached_query(ttl_seconds=7200)  # Cache for 2 hours
    def get_available_parameters(self) -> List[Tuple[str, str]]:
        """Get available parameters with caching."""
        return self.repository.get_available_parameters()

    @cached_query(ttl_seconds=1800)  # Cache for 30 minutes
    def get_data_completeness(
        self, parameter_id: ParameterId, start_date: date, end_date: date
    ) -> float:
        """Get data completeness with caching."""
        return self.repository.get_data_completeness(parameter_id, start_date, end_date)

    def insert_or_replace_data_point(
        self, parameter_id: ParameterId, date: date, value: float, data_source: str
    ) -> None:
        """Insert or replace data point and invalidate cache."""
        # Clear cache for this parameter
        cache_pattern = f"%{parameter_id.name}%{parameter_id.geographic_code}%"
        self.cache.invalidate(cache_pattern)

        return self.repository.insert_or_replace_data_point(
            parameter_id, date, value, data_source
        )


class CachedForecastRepository:
    """Forecast repository with intelligent caching."""

    def __init__(self, db_path: str):
        self.repository = SQLiteForecastRepository(db_path)
        self.cache = get_query_cache()

    def save_forecast(self, forecast_result: ForecastResult) -> None:
        """Save forecast and invalidate related cache entries."""
        # Clear cache entries related to this parameter forecast
        cache_pattern = f"%{forecast_result.parameter_id.name}%{forecast_result.parameter_id.geographic_code}%forecast%"
        self.cache.invalidate(cache_pattern)

        return self.repository.save_forecast(forecast_result)

    @cached_query(ttl_seconds=1800)  # Cache for 30 minutes
    def get_cached_forecast(
        self,
        parameter_id: ParameterId,
        horizon_years: int,
        model_type: str,
        max_age_days: int = 30,
    ) -> Optional[ForecastResult]:
        """Get cached forecast with caching."""
        return self.repository.get_cached_forecast(
            parameter_id, horizon_years, model_type, max_age_days
        )

    @cached_query(ttl_seconds=3600)  # Cache for 1 hour
    def get_forecasts_for_simulation(
        self,
        parameter_names: List[str],
        geographic_code: str,
        horizon_years: int,
        max_age_days: int = 30,
    ) -> Dict[str, ForecastResult]:
        """Get forecasts for simulation with caching."""
        return self.repository.get_forecasts_for_simulation(
            parameter_names, geographic_code, horizon_years, max_age_days
        )

    def delete_old_forecasts(self, days_to_keep: int = 90) -> int:
        """Delete old forecasts and clear cache."""
        # Clear all forecast cache entries
        self.cache.invalidate("%forecast%")

        return self.repository.delete_old_forecasts(days_to_keep)


class CachedCorrelationRepository:
    """Correlation repository with intelligent caching."""

    def __init__(self, db_path: str):
        self.repository = SQLiteCorrelationRepository(db_path)
        self.cache = get_query_cache()

    def save_correlation_matrix(
        self,
        geographic_code: str,
        correlation_matrix: List[List[float]],
        parameter_names: List[str],
        calculation_date: date,
        window_years: int,
    ) -> None:
        """Save correlation matrix and invalidate cache."""
        # Clear cache entries for this geography
        cache_pattern = f"%{geographic_code}%correlation%"
        self.cache.invalidate(cache_pattern)

        return self.repository.save_correlation_matrix(
            geographic_code,
            correlation_matrix,
            parameter_names,
            calculation_date,
            window_years,
        )

    @cached_query(ttl_seconds=3600)  # Cache for 1 hour
    def get_correlation_matrix(
        self, geographic_code: str, parameter_names: List[str], max_age_days: int = 90
    ) -> Optional[Tuple[List[List[float]], List[str], date]]:
        """Get correlation matrix with caching."""
        return self.repository.get_correlation_matrix(
            geographic_code, parameter_names, max_age_days
        )


class CachedDatabaseManager:
    """Database manager that provides cached access to all repositories."""

    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize cached database manager.

        Args:
            db_config: Dictionary mapping database names to file paths
        """
        self.db_config = db_config
        self._repositories = {}

        # Initialize cached repositories
        for db_name, db_path in db_config.items():
            self._repositories[db_name] = {
                "parameter": CachedParameterRepository(db_path),
                "forecast": CachedForecastRepository(db_path),
                "correlation": CachedCorrelationRepository(db_path),
            }

    def get_parameter_repository(self, db_name: str) -> CachedParameterRepository:
        """Get cached parameter repository for database."""
        if db_name not in self._repositories:
            raise ValueError(f"Unknown database: {db_name}")
        return self._repositories[db_name]["parameter"]

    def get_forecast_repository(self, db_name: str) -> CachedForecastRepository:
        """Get cached forecast repository for database."""
        if db_name not in self._repositories:
            raise ValueError(f"Unknown database: {db_name}")
        return self._repositories[db_name]["forecast"]

    def get_correlation_repository(self, db_name: str) -> CachedCorrelationRepository:
        """Get cached correlation repository for database."""
        if db_name not in self._repositories:
            raise ValueError(f"Unknown database: {db_name}")
        return self._repositories[db_name]["correlation"]

    @cached_query(ttl_seconds=1800)  # Cache for 30 minutes
    def get_parameter_data(
        self,
        parameter_name: str,
        geographic_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, any]]:
        """
        Get parameter data across all databases with caching.

        This method searches across all databases to find the parameter data,
        which is useful for the unified data access pattern used in the application.
        """
        results = []

        # Search across all databases for the parameter
        for db_name, repos in self._repositories.items():
            try:
                parameter_id = ParameterId(
                    name=parameter_name,
                    geographic_code=geographic_code,
                    parameter_type=None,  # Will be determined by repository
                )

                start_date_obj = date.fromisoformat(start_date) if start_date else None
                end_date_obj = date.fromisoformat(end_date) if end_date else None

                historical_data = repos["parameter"].get_historical_data(
                    parameter_id, start_date_obj, end_date_obj
                )

                if historical_data and historical_data.data_points:
                    for data_point in historical_data.data_points:
                        results.append(
                            {
                                "date": data_point.date.isoformat(),
                                "value": data_point.value,
                                "data_source": data_point.data_source,
                            }
                        )

            except Exception:
                # Continue searching in other databases
                continue

        # Sort by date
        results.sort(key=lambda x: x["date"])
        return results

    def invalidate_parameter_cache(
        self, parameter_name: str, geographic_code: Optional[str] = None
    ) -> int:
        """Invalidate cache entries for a specific parameter."""
        cache = get_query_cache()

        if geographic_code:
            pattern = f"%{parameter_name}%{geographic_code}%"
        else:
            pattern = f"%{parameter_name}%"

        return cache.invalidate(pattern)

    def cleanup_cache(self) -> int:
        """Clean up expired cache entries."""
        cache = get_query_cache()
        return cache.cleanup_expired()

    def get_cache_statistics(self) -> Dict[str, any]:
        """Get cache performance statistics."""
        cache = get_query_cache()
        return cache.get_cache_stats()


# Factory function for creating cached database manager
def create_cached_database_manager() -> CachedDatabaseManager:
    """Create a cached database manager with standard configuration."""

    db_dir = Path(__file__).parent.parent.parent.parent / "data" / "databases"

    db_config = {
        "market_data": str(db_dir / "market_data.db"),
        "property_data": str(db_dir / "property_data.db"),
        "economic_data": str(db_dir / "economic_data.db"),
        "forecast_cache": str(db_dir / "forecast_cache.db"),
    }

    return CachedDatabaseManager(db_config)
