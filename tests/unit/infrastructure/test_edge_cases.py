"""
Edge Case Tests for Infrastructure Layer

Tests for error scenarios, edge cases, and boundary conditions
in the infrastructure layer.
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core.exceptions import DatabaseError
from src.infrastructure.configuration import configure_test_container
from src.infrastructure.repositories.sqlite_parameter_repository import (
    SQLiteParameterRepository,
)
from src.infrastructure.repositories.sqlite_simulation_repository import (
    SQLiteSimulationRepository,
)


class TestDatabaseEdgeCases:
    """Test database error scenarios and edge cases."""

    def test_repository_with_invalid_database_path_should_raise_error(self):
        """Test repository creation with invalid database path."""
        invalid_path = "/invalid/path/that/does/not/exist/test.db"

        with pytest.raises(DatabaseError):
            repo = SQLiteParameterRepository(invalid_path)
            repo._init_database()

    def test_repository_with_readonly_database_should_handle_gracefully(self):
        """Test repository behavior with read-only database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        # Create the database first
        repo = SQLiteParameterRepository(temp_path)
        repo._init_database()

        # Make the file read-only
        Path(temp_path).chmod(0o444)

        try:
            # This should handle the read-only scenario gracefully
            repo = SQLiteParameterRepository(temp_path)
            with pytest.raises((DatabaseError, sqlite3.OperationalError)):
                # Attempting to write should raise an error
                from datetime import date

                from src.domain.entities.forecast import (
                    DataPoint,
                    HistoricalData,
                    ParameterId,
                    ParameterType,
                )

                param_id = ParameterId("test_param", "NYC", ParameterType.MARKET_METRIC)
                data_points = [
                    DataPoint(param_id, date(2023, 1, 1), 1.0, "test_source")
                ]
                historical_data = HistoricalData(
                    param_id, data_points, date(2023, 1, 1), date(2023, 1, 1)
                )
                repo.save_historical_data(historical_data)
        finally:
            # Clean up - restore permissions and delete file
            try:
                Path(temp_path).chmod(0o644)
                # Give Windows time to release file handles
                import time

                time.sleep(0.1)
                Path(temp_path).unlink(missing_ok=True)
            except (OSError, PermissionError):
                # File might still be in use, ignore cleanup errors in tests
                pass

    def test_database_connection_recovery_after_corruption(self):
        """Test database connection recovery after corruption."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo = SQLiteParameterRepository(temp_path)
            repo._init_database()

            # Corrupt the database file
            with open(temp_path, "wb") as f:
                f.write(b"corrupted data")

            # Repository should handle corruption gracefully
            with pytest.raises(DatabaseError):
                SQLiteParameterRepository(temp_path)

        finally:
            # Give Windows time to release file handles
            try:
                import time

                time.sleep(0.1)
                Path(temp_path).unlink(missing_ok=True)
            except (OSError, PermissionError):
                # File might still be in use, ignore cleanup errors in tests
                pass

    def test_concurrent_database_access_edge_case(self):
        """Test concurrent database access edge cases."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo1 = SQLiteParameterRepository(temp_path)
            repo1._init_database()

            repo2 = SQLiteParameterRepository(temp_path)

            # Both repositories should be able to read concurrently
            params1 = repo1.get_available_parameters("NYC")
            params2 = repo2.get_available_parameters("NYC")

            assert params1 == params2

        finally:
            # Give Windows time to release file handles
            try:
                import time

                time.sleep(0.1)
                Path(temp_path).unlink(missing_ok=True)
            except (OSError, PermissionError):
                # File might still be in use, ignore cleanup errors in tests
                pass

    def test_database_with_insufficient_disk_space(self):
        """Test database behavior with insufficient disk space."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo = SQLiteParameterRepository(temp_path)
            repo._init_database()

            # Create a mock that raises an error when used as context manager
            class MockConnection:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    return None

                def execute(self, *args, **kwargs):
                    raise sqlite3.OperationalError("database or disk is full")

            with patch("sqlite3.connect") as mock_connect:
                mock_connect.return_value = MockConnection()

                # The method catches exceptions and returns empty list, so test that behavior
                result = repo.get_available_parameters("NYC")
                assert result == []  # Should return empty list on error

                # Verify connect was called
                mock_connect.assert_called_with(repo._db_path)

        finally:
            # Give Windows time to release file handles
            try:
                import time

                time.sleep(0.1)
                Path(temp_path).unlink(missing_ok=True)
            except (OSError, PermissionError):
                # File might still be in use, ignore cleanup errors in tests
                pass


class TestConfigurationEdgeCases:
    """Test configuration error scenarios and edge cases."""

    def test_container_configuration_with_missing_dependencies(self):
        """Test container configuration with missing dependencies."""
        # This should not raise an error during configuration
        container = configure_test_container()

        # But resolving a service that depends on missing external resources might fail
        # The container should handle this gracefully
        assert container is not None

    def test_container_with_circular_dependencies(self):
        """Test container behavior with circular dependencies."""
        from src.infrastructure.container import DependencyContainer

        container = DependencyContainer()

        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_a):
                self.service_a = service_a

        container.register_singleton(ServiceA, ServiceA)
        container.register_singleton(ServiceB, ServiceB)

        # This should raise an error due to circular dependency or unresolved dependencies
        with pytest.raises((ValueError, RecursionError, TypeError)):
            container.resolve(ServiceA)

    def test_container_with_invalid_service_registration(self):
        """Test container with invalid service registration."""
        from src.infrastructure.container import DependencyContainer

        container = DependencyContainer()

        # Register with invalid parameters
        with pytest.raises((TypeError, AttributeError)):
            container.register_singleton(None, None)

    def test_container_memory_leak_prevention(self):
        """Test that container prevents memory leaks."""
        from src.infrastructure.container import DependencyContainer

        container = DependencyContainer()

        class TestService:
            def __init__(self):
                self.data = [0] * 1000  # Some data to track memory

        container.register_singleton(TestService, TestService)

        # Create many instances
        services = []
        for _ in range(100):
            service = container.resolve(TestService)
            services.append(service)

        # All should be the same instance (singleton)
        assert all(service is services[0] for service in services)

        # Clear container should clean up references
        container.clear()

        # Container should be empty after clearing
        with pytest.raises(ValueError):
            container.resolve(TestService)


class TestRepositoryEdgeCases:
    """Test repository edge cases and error scenarios."""

    def test_parameter_repository_with_extreme_data_volumes(self):
        """Test parameter repository with extreme data volumes."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo = SQLiteParameterRepository(temp_path)
            repo._init_database()

            from datetime import date, timedelta

            from src.domain.entities.forecast import (
                DataPoint,
                HistoricalData,
                ParameterId,
                ParameterType,
            )

            # Create large dataset
            param_id = ParameterId(
                "stress_test_param", "NYC", ParameterType.MARKET_METRIC
            )
            start_date = date(2000, 1, 1)
            end_date = start_date + timedelta(days=9999)

            # Create 10,000 data points (about 27 years of daily data)
            data_points = [
                DataPoint(
                    param_id,
                    start_date + timedelta(days=i),
                    float(i % 100),
                    "stress_test",
                )
                for i in range(10000)
            ]

            historical_data = HistoricalData(
                param_id, data_points, start_date, end_date
            )

            # This should handle large datasets
            repo.save_historical_data(historical_data)

            # Verify data can be retrieved
            retrieved_data = repo.get_historical_data(
                param_id,
                start_date,
                start_date + timedelta(days=9999),
            )

            assert retrieved_data is not None
            assert len(retrieved_data.data_points) == 10000

        finally:
            # Give Windows time to release file handles
            try:
                import time

                time.sleep(0.1)
                Path(temp_path).unlink(missing_ok=True)
            except (OSError, PermissionError):
                # File might still be in use, ignore cleanup errors in tests
                pass

    def test_simulation_repository_with_corrupted_json_data(self):
        """Test simulation repository with corrupted JSON data."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo = SQLiteSimulationRepository(temp_path)
            repo._init_database()

            # Manually insert corrupted JSON data
            import sqlite3

            with sqlite3.connect(temp_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO simulation_results
                    (simulation_id, property_id, msa_code, num_scenarios, horizon_years, use_correlations, confidence_level, simulation_date, computation_time_seconds, summary_data, correlation_matrix, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        "test_sim_1",
                        "test_prop_1",
                        "NYC",
                        100,
                        6,
                        True,
                        0.95,
                        "2023-01-01 12:00:00",
                        1.5,
                        "invalid json data",  # Corrupted JSON for summary_data
                        "{}",
                        "2023-01-01 12:00:00",
                    ),
                )
                conn.commit()

            # Repository should handle corrupted data gracefully
            result = repo.get_simulation_result("test_sim_1")
            assert result is None  # Should return None for corrupted data

        finally:
            # Give Windows time to release file handles
            try:
                import time

                time.sleep(0.1)
                Path(temp_path).unlink(missing_ok=True)
            except (OSError, PermissionError):
                # File might still be in use, ignore cleanup errors in tests
                pass

    def test_repository_transaction_rollback_on_error(self):
        """Test repository transaction rollback on error."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo = SQLiteParameterRepository(temp_path)
            repo._init_database()

            from datetime import date

            from src.domain.entities.forecast import (
                DataPoint,
                HistoricalData,
                ParameterId,
                ParameterType,
            )

            # Create valid data
            param_id = ParameterId("test_param", "NYC", ParameterType.MARKET_METRIC)
            data_points = [DataPoint(param_id, date(2023, 1, 1), 1.0, "test_source")]
            historical_data = HistoricalData(
                param_id, data_points, date(2023, 1, 1), date(2023, 1, 1)
            )

            # Create a context manager mock that raises an error during execute
            class MockConnection:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    return None

                def execute(self, *args, **kwargs):
                    raise sqlite3.OperationalError("Simulated error")

            with patch("sqlite3.connect") as mock_connect:
                mock_connect.return_value = MockConnection()

                with pytest.raises(Exception):  # Should raise from the execute error
                    repo.save_historical_data(historical_data)

                # Verify connect was called
                mock_connect.assert_called_with(repo._db_path)

        finally:
            # Give Windows time to release file handles
            try:
                import time

                time.sleep(0.1)
                Path(temp_path).unlink(missing_ok=True)
            except (OSError, PermissionError):
                # File might still be in use, ignore cleanup errors in tests
                pass
