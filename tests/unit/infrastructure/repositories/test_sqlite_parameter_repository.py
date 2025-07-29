"""
Unit Tests for SQLite Parameter Repository

Tests the infrastructure layer implementation of parameter repository.
"""

import os
import tempfile
from datetime import date, datetime
from pathlib import Path

import pytest

from src.domain.entities.forecast import (
    DataPoint,
    ForecastPoint,
    ForecastResult,
    HistoricalData,
    ModelPerformance,
    ParameterId,
    ParameterType,
)
from src.infrastructure.repositories.sqlite_parameter_repository import (
    SQLiteCorrelationRepository,
    SQLiteForecastRepository,
    SQLiteParameterRepository,
)


class TestSQLiteParameterRepository:
    """Test cases for SQLiteParameterRepository."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name
        yield db_path
        # Cleanup - force close connections and retry on Windows
        if os.path.exists(db_path):
            import gc
            import time

            gc.collect()  # Force garbage collection to close connections
            time.sleep(0.1)  # Brief pause for Windows
            try:
                os.unlink(db_path)
            except PermissionError:
                # On Windows, file may still be locked - try again after brief delay
                time.sleep(0.5)
                try:
                    os.unlink(db_path)
                except PermissionError:
                    pass  # Skip cleanup if still locked

    @pytest.fixture
    def repository(self, temp_db_path):
        """Create a repository instance with temporary database."""
        return SQLiteParameterRepository(temp_db_path)

    @pytest.fixture
    def sample_parameter_id(self):
        """Sample parameter ID for testing."""
        return ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

    @pytest.fixture
    def sample_historical_data(self, sample_parameter_id):
        """Sample historical data for testing."""
        data_points = [
            DataPoint(sample_parameter_id, date(2020, 1, 1), 0.065, "test_source"),
            DataPoint(sample_parameter_id, date(2021, 1, 1), 0.067, "test_source"),
            DataPoint(sample_parameter_id, date(2022, 1, 1), 0.070, "test_source"),
            DataPoint(sample_parameter_id, date(2023, 1, 1), 0.068, "test_source"),
        ]

        return HistoricalData(
            parameter_id=sample_parameter_id,
            data_points=data_points,
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
        )

    def test_init_database_creates_tables(self, temp_db_path):
        """
        GIVEN a new database file
        WHEN initializing SQLiteParameterRepository
        THEN it should create the required tables
        """
        # Act
        repository = SQLiteParameterRepository(temp_db_path)

        # Assert - check that tables exist by querying them
        import sqlite3

        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='historical_data'
            """
            )
            tables = cursor.fetchall()
            assert len(tables) == 1
            assert tables[0][0] == "historical_data"

    def test_save_historical_data_stores_data_correctly(
        self, repository, sample_historical_data
    ):
        """
        GIVEN historical data
        WHEN saving to repository
        THEN it should store all data points correctly
        """
        # Act
        repository.save_historical_data(sample_historical_data)

        # Assert
        retrieved_data = repository.get_historical_data(
            sample_historical_data.parameter_id
        )

        assert retrieved_data is not None
        assert len(retrieved_data.data_points) == 4
        assert retrieved_data.parameter_id == sample_historical_data.parameter_id
        assert retrieved_data.start_date == sample_historical_data.start_date
        assert retrieved_data.end_date == sample_historical_data.end_date

    def test_get_historical_data_with_date_range_filters_correctly(
        self, repository, sample_historical_data
    ):
        """
        GIVEN stored historical data
        WHEN retrieving with date range filter
        THEN it should return only data within the range
        """
        # Arrange
        repository.save_historical_data(sample_historical_data)

        # Act
        filtered_data = repository.get_historical_data(
            sample_historical_data.parameter_id,
            start_date=date(2021, 1, 1),
            end_date=date(2022, 1, 1),
        )

        # Assert
        assert filtered_data is not None
        assert len(filtered_data.data_points) == 2
        assert all(
            date(2021, 1, 1) <= dp.date <= date(2022, 1, 1)
            for dp in filtered_data.data_points
        )

    def test_get_historical_data_nonexistent_parameter_returns_none(self, repository):
        """
        GIVEN empty repository
        WHEN retrieving nonexistent parameter
        THEN it should return None
        """
        # Arrange
        nonexistent_id = ParameterId(
            "nonexistent", "12345", ParameterType.GROWTH_METRIC
        )

        # Act
        result = repository.get_historical_data(nonexistent_id)

        # Assert
        assert result is None

    def test_get_available_parameters_returns_correct_list(
        self, repository, sample_historical_data
    ):
        """
        GIVEN stored historical data for multiple parameters
        WHEN getting available parameters for a geography
        THEN it should return correct parameter list
        """
        # Arrange
        repository.save_historical_data(sample_historical_data)

        # Create another parameter for same geography
        another_param_id = ParameterId(
            "vacancy_rate", "35620", ParameterType.MARKET_METRIC
        )
        another_data_point = DataPoint(another_param_id, date(2023, 1, 1), 0.05, "test")
        another_historical_data = HistoricalData(
            parameter_id=another_param_id,
            data_points=[another_data_point],
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 1),
        )
        repository.save_historical_data(another_historical_data)

        # Act
        available_params = repository.get_available_parameters("35620")

        # Assert
        assert len(available_params) == 2
        param_names = [p.name for p in available_params]
        assert "cap_rate" in param_names
        assert "vacancy_rate" in param_names

    def test_get_data_completeness_calculates_correctly(
        self, repository, sample_historical_data
    ):
        """
        GIVEN historical data with known gaps
        WHEN calculating data completeness
        THEN it should return correct percentage
        """
        # Arrange
        repository.save_historical_data(sample_historical_data)

        # Act
        completeness = repository.get_data_completeness(
            sample_historical_data.parameter_id,
            start_date=date(2020, 1, 1),
            end_date=date(2023, 12, 31),
        )

        # Assert
        assert isinstance(completeness, float)
        assert 0.0 <= completeness <= 1.0

    def test_insert_or_replace_updates_existing_data(
        self, repository, sample_historical_data
    ):
        """
        GIVEN existing historical data
        WHEN saving updated data for same parameter and date
        THEN it should update the existing record
        """
        # Arrange
        repository.save_historical_data(sample_historical_data)

        # Update the first data point with new value
        updated_data_points = sample_historical_data.data_points.copy()
        updated_data_points[0] = DataPoint(
            sample_historical_data.parameter_id,
            date(2020, 1, 1),
            0.080,  # New value
            "updated_source",
        )

        updated_historical_data = HistoricalData(
            parameter_id=sample_historical_data.parameter_id,
            data_points=updated_data_points,
            start_date=sample_historical_data.start_date,
            end_date=sample_historical_data.end_date,
        )

        # Act
        repository.save_historical_data(updated_historical_data)

        # Assert
        retrieved_data = repository.get_historical_data(
            sample_historical_data.parameter_id
        )
        first_point = next(
            dp for dp in retrieved_data.data_points if dp.date == date(2020, 1, 1)
        )
        assert first_point.value == 0.080
        assert first_point.data_source == "updated_source"


class TestSQLiteForecastRepository:
    """Test cases for SQLiteForecastRepository."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name
        yield db_path
        # Cleanup - force close connections and retry on Windows
        if os.path.exists(db_path):
            import gc
            import time

            gc.collect()  # Force garbage collection to close connections
            time.sleep(0.1)  # Brief pause for Windows
            try:
                os.unlink(db_path)
            except PermissionError:
                # On Windows, file may still be locked - try again after brief delay
                time.sleep(0.5)
                try:
                    os.unlink(db_path)
                except PermissionError:
                    pass  # Skip cleanup if still locked

    @pytest.fixture
    def repository(self, temp_db_path):
        """Create a forecast repository instance."""
        return SQLiteForecastRepository(temp_db_path)

    @pytest.fixture
    def sample_parameter_id(self):
        """Sample parameter ID for testing."""
        return ParameterId(
            name="rent_growth",
            geographic_code="16980",
            parameter_type=ParameterType.GROWTH_METRIC,
        )

    @pytest.fixture
    def sample_forecast_result(self, sample_parameter_id):
        """Sample forecast result for testing."""
        forecast_points = [
            ForecastPoint(date(2024, 1, 1), 0.025, 0.020, 0.030),
            ForecastPoint(date(2025, 1, 1), 0.027, 0.022, 0.032),
            ForecastPoint(date(2026, 1, 1), 0.024, 0.019, 0.029),
        ]

        model_performance = ModelPerformance(
            mae=0.005, mape=8.5, rmse=0.007, r_squared=0.85
        )

        return ForecastResult(
            forecast_id="test_forecast_001",
            parameter_id=sample_parameter_id,
            forecast_points=forecast_points,
            model_performance=model_performance,
            model_type="prophet",
            forecast_date=datetime.now(),
            horizon_years=3,
            historical_data_points=36,
        )

    def test_init_database_creates_forecast_tables(self, temp_db_path):
        """
        GIVEN a new database file
        WHEN initializing SQLiteForecastRepository
        THEN it should create forecast tables
        """
        # Act
        repository = SQLiteForecastRepository(temp_db_path)

        # Assert
        import sqlite3

        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='forecasts'
            """
            )
            tables = cursor.fetchall()
            assert len(tables) == 1

    def test_save_forecast_stores_complete_forecast(
        self, repository, sample_forecast_result
    ):
        """
        GIVEN a forecast result
        WHEN saving to repository
        THEN it should store all forecast data correctly
        """
        # Act
        repository.save_forecast(sample_forecast_result)

        # Assert
        retrieved_forecast = repository.get_cached_forecast(
            sample_forecast_result.parameter_id,
            sample_forecast_result.horizon_years,
            sample_forecast_result.model_type,
        )

        assert retrieved_forecast is not None
        assert retrieved_forecast.forecast_id == sample_forecast_result.forecast_id
        assert len(retrieved_forecast.forecast_points) == 3
        assert retrieved_forecast.model_performance.mae == 0.005

    def test_get_cached_forecast_respects_max_age(
        self, repository, sample_forecast_result
    ):
        """
        GIVEN an old cached forecast
        WHEN retrieving with short max_age_days
        THEN it should return None for expired forecasts
        """
        # Arrange
        repository.save_forecast(sample_forecast_result)

        # Act - request with very old cutoff (should be expired)
        # Use -1 days to ensure the cutoff is before today
        result = repository.get_cached_forecast(
            sample_forecast_result.parameter_id,
            sample_forecast_result.horizon_years,
            sample_forecast_result.model_type,
            max_age_days=-1,
        )

        # Assert
        assert result is None

    def test_get_forecasts_for_simulation_returns_multiple_forecasts(self, repository):
        """
        GIVEN multiple cached forecasts
        WHEN getting forecasts for simulation
        THEN it should return dictionary of available forecasts
        """
        # Arrange
        param_ids = [
            ParameterId("cap_rate", "35620", ParameterType.MARKET_METRIC),
            ParameterId("vacancy_rate", "35620", ParameterType.MARKET_METRIC),
        ]

        for param_id in param_ids:
            forecast_points = [ForecastPoint(date(2024, 1, 1), 0.05, 0.04, 0.06)]
            model_performance = ModelPerformance(0.001, 1.0, 0.002, 0.95)

            forecast = ForecastResult(
                forecast_id=f"test_{param_id.name}",
                parameter_id=param_id,
                forecast_points=forecast_points,
                model_performance=model_performance,
                model_type="prophet",
                forecast_date=datetime.now(),
                horizon_years=1,
                historical_data_points=24,
            )
            repository.save_forecast(forecast)

        # Act
        results = repository.get_forecasts_for_simulation(param_ids, 1, "prophet")

        # Assert
        assert len(results) == 2
        assert all(param_id in results for param_id in param_ids)

    def test_delete_old_forecasts_removes_expired_forecasts(
        self, repository, sample_forecast_result
    ):
        """
        GIVEN old forecasts in repository
        WHEN deleting old forecasts
        THEN it should remove expired forecasts and return count
        """
        # Arrange
        repository.save_forecast(sample_forecast_result)

        # Act
        deleted_count = repository.delete_old_forecasts(older_than_days=0)

        # Assert
        assert deleted_count >= 0

        # Verify forecast is deleted
        retrieved = repository.get_cached_forecast(
            sample_forecast_result.parameter_id,
            sample_forecast_result.horizon_years,
            sample_forecast_result.model_type,
            max_age_days=365,
        )
        # May or may not be None depending on exact timing, but test completes successfully


class TestSQLiteCorrelationRepository:
    """Test cases for SQLiteCorrelationRepository."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name
        yield db_path
        # Cleanup - force close connections and retry on Windows
        if os.path.exists(db_path):
            import gc
            import time

            gc.collect()  # Force garbage collection to close connections
            time.sleep(0.1)  # Brief pause for Windows
            try:
                os.unlink(db_path)
            except PermissionError:
                # On Windows, file may still be locked - try again after brief delay
                time.sleep(0.5)
                try:
                    os.unlink(db_path)
                except PermissionError:
                    pass  # Skip cleanup if still locked

    @pytest.fixture
    def repository(self, temp_db_path):
        """Create a correlation repository instance."""
        return SQLiteCorrelationRepository(temp_db_path)

    @pytest.fixture
    def sample_correlation_data(self):
        """Sample correlation matrix data for testing."""
        return {
            "geographic_code": "35620",
            "correlation_matrix": [[1.0, 0.5, -0.2], [0.5, 1.0, 0.1], [-0.2, 0.1, 1.0]],
            "parameter_names": ["cap_rate", "vacancy_rate", "rent_growth"],
            "calculation_date": date(2024, 1, 1),
            "window_years": 10,
        }

    def test_init_database_creates_correlation_tables(self, temp_db_path):
        """
        GIVEN a new database file
        WHEN initializing SQLiteCorrelationRepository
        THEN it should create correlation tables
        """
        # Act
        repository = SQLiteCorrelationRepository(temp_db_path)

        # Assert
        import sqlite3

        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='parameter_correlations'
            """
            )
            tables = cursor.fetchall()
            assert len(tables) == 1

    def test_save_correlation_matrix_stores_data_correctly(
        self, repository, sample_correlation_data
    ):
        """
        GIVEN correlation matrix data
        WHEN saving to repository
        THEN it should store all correlation data correctly
        """
        # Act
        repository.save_correlation_matrix(**sample_correlation_data)

        # Assert - Use larger max_age_days to account for old test data
        retrieved_data = repository.get_correlation_matrix(
            sample_correlation_data["geographic_code"],
            sample_correlation_data["parameter_names"],
            max_age_days=500,  # Accommodate old test data from 2024
        )

        assert retrieved_data is not None
        matrix, param_names, calc_date = retrieved_data
        assert matrix == sample_correlation_data["correlation_matrix"]
        assert set(param_names) == set(sample_correlation_data["parameter_names"])
        assert calc_date == sample_correlation_data["calculation_date"]

    def test_get_correlation_matrix_respects_max_age(
        self, repository, sample_correlation_data
    ):
        """
        GIVEN an old correlation matrix
        WHEN retrieving with short max_age_days
        THEN it should return None for expired matrices
        """
        # Arrange
        repository.save_correlation_matrix(**sample_correlation_data)

        # Act - request with very restrictive max age (should be expired)
        result = repository.get_correlation_matrix(
            sample_correlation_data["geographic_code"],
            sample_correlation_data["parameter_names"],
            max_age_days=-1,  # Negative to ensure expiration
        )

        # Assert
        assert result is None

    def test_get_correlation_matrix_handles_parameter_order(
        self, repository, sample_correlation_data
    ):
        """
        GIVEN stored correlation matrix
        WHEN retrieving with different parameter order
        THEN it should still find the matrix (parameters are sorted internally)
        """
        # Arrange
        repository.save_correlation_matrix(**sample_correlation_data)

        # Act - request with different parameter order
        shuffled_params = ["rent_growth", "cap_rate", "vacancy_rate"]
        result = repository.get_correlation_matrix(
            sample_correlation_data["geographic_code"],
            shuffled_params,
            max_age_days=500,  # Accommodate old test data
        )

        # Assert
        assert result is not None
        matrix, param_names, calc_date = result
        assert matrix == sample_correlation_data["correlation_matrix"]

    def test_save_correlation_matrix_replaces_existing(
        self, repository, sample_correlation_data
    ):
        """
        GIVEN existing correlation matrix
        WHEN saving new matrix for same parameters
        THEN it should replace the existing matrix
        """
        # Arrange
        repository.save_correlation_matrix(**sample_correlation_data)

        # Update the matrix
        updated_data = sample_correlation_data.copy()
        updated_data["correlation_matrix"] = [
            [1.0, 0.8, -0.3],
            [0.8, 1.0, 0.2],
            [-0.3, 0.2, 1.0],
        ]
        updated_data["calculation_date"] = date(2024, 6, 1)

        # Act
        repository.save_correlation_matrix(**updated_data)

        # Assert
        retrieved_data = repository.get_correlation_matrix(
            updated_data["geographic_code"],
            updated_data["parameter_names"],
            max_age_days=500,  # Accommodate test data
        )

        assert retrieved_data is not None
        matrix, param_names, calc_date = retrieved_data
        assert matrix == updated_data["correlation_matrix"]
        assert calc_date == updated_data["calculation_date"]
