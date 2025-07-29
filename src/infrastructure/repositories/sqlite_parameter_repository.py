"""
SQLite Implementation of Parameter Repository

Concrete implementation of parameter repository using SQLite database.
"""

import json
import logging
import sqlite3
from dataclasses import asdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from ...domain.entities.forecast import (
    DataPoint,
    ForecastPoint,
    ForecastResult,
    HistoricalData,
    ModelPerformance,
    ParameterId,
    ParameterType,
)
from ...domain.repositories.parameter_repository import (
    CorrelationRepository,
    ForecastRepository,
    ParameterRepository,
)


class SQLiteParameterRepository(ParameterRepository):
    """SQLite implementation of parameter repository."""

    def __init__(self, database_path: str, logger: Optional[logging.Logger] = None):
        self._db_path = database_path
        self._logger = logger or logging.getLogger(__name__)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS historical_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parameter_name TEXT NOT NULL,
                    geographic_code TEXT NOT NULL,
                    parameter_type TEXT NOT NULL,
                    date TEXT NOT NULL,
                    value REAL NOT NULL,
                    data_source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(parameter_name, geographic_code, date)
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_historical_data_lookup
                ON historical_data(parameter_name, geographic_code, date)
            """
            )

    def get_historical_data(
        self,
        parameter_id: ParameterId,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[HistoricalData]:
        """Retrieve historical data for a parameter."""
        query = """
            SELECT date, value, data_source
            FROM historical_data
            WHERE parameter_name = ? AND geographic_code = ?
        """
        params = [parameter_id.name, parameter_id.geographic_code]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY date"

        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                if not rows:
                    return None

                data_points = []
                for date_str, value, data_source in rows:
                    data_point = DataPoint(
                        parameter_id=parameter_id,
                        date=date.fromisoformat(date_str),
                        value=float(value),
                        data_source=data_source,
                    )
                    data_points.append(data_point)

                return HistoricalData(
                    parameter_id=parameter_id,
                    data_points=data_points,
                    start_date=data_points[0].date,
                    end_date=data_points[-1].date,
                )

        except Exception as e:
            self._logger.error(f"Failed to retrieve historical data: {e}")
            return None

    def save_historical_data(self, historical_data: HistoricalData) -> None:
        """Save historical data for a parameter."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                for data_point in historical_data.data_points:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO historical_data
                        (parameter_name, geographic_code, parameter_type, date, value, data_source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            data_point.parameter_id.name,
                            data_point.parameter_id.geographic_code,
                            data_point.parameter_id.parameter_type.value,
                            data_point.date.isoformat(),
                            data_point.value,
                            data_point.data_source,
                            datetime.now().isoformat(),
                        ),
                    )

                self._logger.info(
                    f"Saved {len(historical_data.data_points)} data points for "
                    f"{historical_data.parameter_id.name}"
                )

        except Exception as e:
            self._logger.error(f"Failed to save historical data: {e}")
            raise

    def get_available_parameters(self, geographic_code: str) -> List[ParameterId]:
        """Get all available parameters for a geographic area."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT DISTINCT parameter_name, parameter_type
                    FROM historical_data
                    WHERE geographic_code = ?
                """,
                    (geographic_code,),
                )

                rows = cursor.fetchall()

                parameter_ids = []
                for param_name, param_type_str in rows:
                    parameter_id = ParameterId(
                        name=param_name,
                        geographic_code=geographic_code,
                        parameter_type=ParameterType(param_type_str),
                    )
                    parameter_ids.append(parameter_id)

                return parameter_ids

        except Exception as e:
            self._logger.error(f"Failed to get available parameters: {e}")
            return []

    def get_data_completeness(
        self, parameter_id: ParameterId, start_date: date, end_date: date
    ) -> float:
        """Calculate data completeness percentage for a parameter."""
        try:
            # Calculate expected number of data points (assuming monthly data)
            days_diff = (end_date - start_date).days
            expected_points = max(1, days_diff // 30)  # Rough monthly estimate

            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT COUNT(*)
                    FROM historical_data
                    WHERE parameter_name = ? AND geographic_code = ?
                    AND date >= ? AND date <= ?
                """,
                    (
                        parameter_id.name,
                        parameter_id.geographic_code,
                        start_date.isoformat(),
                        end_date.isoformat(),
                    ),
                )

                actual_points = cursor.fetchone()[0]

                return min(1.0, actual_points / expected_points)

        except Exception as e:
            self._logger.error(f"Failed to calculate data completeness: {e}")
            return 0.0


class SQLiteForecastRepository(ForecastRepository):
    """SQLite implementation of forecast repository."""

    def __init__(self, database_path: str, logger: Optional[logging.Logger] = None):
        self._db_path = database_path
        self._logger = logger or logging.getLogger(__name__)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS forecasts (
                    forecast_id TEXT PRIMARY KEY,
                    parameter_name TEXT NOT NULL,
                    geographic_code TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    horizon_years INTEGER NOT NULL,
                    forecast_data TEXT NOT NULL,  -- JSON
                    model_performance TEXT NOT NULL,  -- JSON
                    historical_data_points INTEGER NOT NULL,
                    forecast_date TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_forecast_lookup
                ON forecasts(parameter_name, geographic_code, model_type, horizon_years)
            """
            )

    def save_forecast(self, forecast_result: ForecastResult) -> None:
        """Save a forecast result."""
        try:
            # Serialize forecast points
            forecast_data = []
            for fp in forecast_result.forecast_points:
                forecast_data.append(
                    {
                        "date": fp.date.isoformat(),
                        "value": fp.value,
                        "lower_bound": fp.lower_bound,
                        "upper_bound": fp.upper_bound,
                    }
                )

            # Serialize model performance
            performance_data = asdict(forecast_result.model_performance)

            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO forecasts
                    (forecast_id, parameter_name, geographic_code, model_type,
                     horizon_years, forecast_data, model_performance,
                     historical_data_points, forecast_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        forecast_result.forecast_id,
                        forecast_result.parameter_id.name,
                        forecast_result.parameter_id.geographic_code,
                        forecast_result.model_type,
                        forecast_result.horizon_years,
                        json.dumps(forecast_data),
                        json.dumps(performance_data),
                        forecast_result.historical_data_points,
                        forecast_result.forecast_date.isoformat(),
                        datetime.now().isoformat(),
                    ),
                )

                self._logger.info(f"Saved forecast {forecast_result.forecast_id}")

        except Exception as e:
            self._logger.error(f"Failed to save forecast: {e}")
            raise

    def get_cached_forecast(
        self,
        parameter_id: ParameterId,
        horizon_years: int,
        model_type: str,
        max_age_days: int = 30,
    ) -> Optional[ForecastResult]:
        """Retrieve a cached forecast if available and not too old."""
        try:
            cutoff_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date - timedelta(days=max_age_days)

            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT forecast_id, forecast_data, model_performance,
                           historical_data_points, forecast_date
                    FROM forecasts
                    WHERE parameter_name = ? AND geographic_code = ?
                    AND model_type = ? AND horizon_years = ?
                    AND created_at >= ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """,
                    (
                        parameter_id.name,
                        parameter_id.geographic_code,
                        model_type,
                        horizon_years,
                        cutoff_date.isoformat(),
                    ),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                (
                    forecast_id,
                    forecast_data_json,
                    performance_json,
                    hist_points,
                    forecast_date_str,
                ) = row

                # Deserialize forecast data
                forecast_data = json.loads(forecast_data_json)
                forecast_points = []
                for fp_data in forecast_data:
                    forecast_point = ForecastPoint(
                        date=date.fromisoformat(fp_data["date"]),
                        value=fp_data["value"],
                        lower_bound=fp_data["lower_bound"],
                        upper_bound=fp_data["upper_bound"],
                    )
                    forecast_points.append(forecast_point)

                # Deserialize performance data
                performance_data = json.loads(performance_json)
                model_performance = ModelPerformance(**performance_data)

                return ForecastResult(
                    forecast_id=forecast_id,
                    parameter_id=parameter_id,
                    forecast_points=forecast_points,
                    model_performance=model_performance,
                    model_type=model_type,
                    forecast_date=datetime.fromisoformat(forecast_date_str),
                    horizon_years=horizon_years,
                    historical_data_points=hist_points,
                )

        except Exception as e:
            self._logger.error(f"Failed to retrieve cached forecast: {e}")
            return None

    def get_forecasts_for_simulation(
        self,
        parameter_ids: List[ParameterId],
        horizon_years: int,
        model_type: str,
        max_age_days: int = 30,
    ) -> Dict[ParameterId, ForecastResult]:
        """Get multiple forecasts for Monte Carlo simulation."""
        results = {}

        for parameter_id in parameter_ids:
            forecast = self.get_cached_forecast(
                parameter_id, horizon_years, model_type, max_age_days
            )
            if forecast:
                results[parameter_id] = forecast

        return results

    def delete_old_forecasts(self, older_than_days: int) -> int:
        """Delete forecasts older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)

            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM forecasts
                    WHERE created_at < ?
                """,
                    (cutoff_date.isoformat(),),
                )

                deleted_count = cursor.rowcount

                if deleted_count > 0:
                    self._logger.info(f"Deleted {deleted_count} old forecasts")

                return deleted_count

        except Exception as e:
            self._logger.error(f"Failed to delete old forecasts: {e}")
            return 0


class SQLiteCorrelationRepository(CorrelationRepository):
    """SQLite implementation of correlation repository."""

    def __init__(self, database_path: str, logger: Optional[logging.Logger] = None):
        self._db_path = database_path
        self._logger = logger or logging.getLogger(__name__)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS parameter_correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    geographic_code TEXT NOT NULL,
                    correlation_matrix TEXT NOT NULL,  -- JSON
                    parameter_names TEXT NOT NULL,     -- JSON
                    calculation_date TEXT NOT NULL,
                    window_years INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(geographic_code, parameter_names, window_years)
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_correlation_lookup
                ON parameter_correlations(geographic_code, calculation_date DESC)
            """
            )

    def save_correlation_matrix(
        self,
        geographic_code: str,
        correlation_matrix: List[List[float]],
        parameter_names: List[str],
        calculation_date: date,
        window_years: int,
    ) -> None:
        """Save a parameter correlation matrix."""
        try:
            # Sort parameter names for consistent storage and retrieval
            sorted_param_names = sorted(parameter_names)
            correlation_matrix_json = json.dumps(correlation_matrix)
            parameter_names_json = json.dumps(sorted_param_names)

            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO parameter_correlations
                    (geographic_code, correlation_matrix, parameter_names,
                     calculation_date, window_years, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        geographic_code,
                        correlation_matrix_json,
                        parameter_names_json,
                        calculation_date.isoformat(),
                        window_years,
                        datetime.now().isoformat(),
                    ),
                )

                self._logger.info(
                    f"Saved correlation matrix for {geographic_code} with {len(parameter_names)} parameters"
                )

        except Exception as e:
            self._logger.error(f"Failed to save correlation matrix: {e}")
            raise

    def get_correlation_matrix(
        self, geographic_code: str, parameter_names: List[str], max_age_days: int = 90
    ) -> Optional[tuple[List[List[float]], List[str], date]]:
        """Retrieve a correlation matrix if available and recent."""
        try:
            cutoff_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date - timedelta(days=max_age_days)

            # Sort parameter names for consistent lookup
            sorted_param_names = sorted(parameter_names)
            parameter_names_json = json.dumps(sorted_param_names)

            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT correlation_matrix, parameter_names, calculation_date
                    FROM parameter_correlations
                    WHERE geographic_code = ?
                    AND parameter_names = ?
                    AND created_at >= ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """,
                    (geographic_code, parameter_names_json, cutoff_date.isoformat()),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                (
                    correlation_matrix_json,
                    stored_param_names_json,
                    calculation_date_str,
                ) = row

                correlation_matrix = json.loads(correlation_matrix_json)
                stored_param_names = json.loads(stored_param_names_json)
                calculation_date = date.fromisoformat(calculation_date_str)

                return (correlation_matrix, stored_param_names, calculation_date)

        except Exception as e:
            self._logger.error(f"Failed to retrieve correlation matrix: {e}")
            return None
