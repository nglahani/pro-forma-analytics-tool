"""
Edge Case Tests for Infrastructure Layer

Tests for error scenarios, edge cases, and boundary conditions
in the infrastructure layer.
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from core.exceptions import ConfigurationError, DatabaseError
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
            with pytest.raises(DatabaseError):
                # Attempting to write should raise an error
                from datetime import date

                from src.domain.entities.forecast import (
                    DataPoint,
                    HistoricalData,
                    ParameterId,
                )

                param_id = ParameterId("test_param", "NYC")
                data_points = [DataPoint(date(2023, 1, 1), 1.0)]
                historical_data = HistoricalData(param_id, data_points)
                repo.save_historical_data(historical_data)
        finally:
            # Clean up
            Path(temp_path).chmod(0o644)
            Path(temp_path).unlink(missing_ok=True)

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
                repo.get_available_parameters()

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_concurrent_database_access_edge_case(self):
        """Test concurrent database access edge cases."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo1 = SQLiteParameterRepository(temp_path)
            repo1._init_database()

            repo2 = SQLiteParameterRepository(temp_path)

            # Both repositories should be able to read concurrently
            params1 = repo1.get_available_parameters()
            params2 = repo2.get_available_parameters()

            assert params1 == params2

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_database_with_insufficient_disk_space(self):
        """Test database behavior with insufficient disk space."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo = SQLiteParameterRepository(temp_path)
            repo._init_database()

            # Mock sqlite3 to simulate disk space error
            with patch("sqlite3.connect") as mock_connect:
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.execute.side_effect = sqlite3.OperationalError(
                    "database or disk is full"
                )
                mock_conn.cursor.return_value = mock_cursor
                mock_connect.return_value = mock_conn

                with pytest.raises(DatabaseError) as exc_info:
                    repo.get_available_parameters()

                assert "database or disk is full" in str(exc_info.value)

        finally:
            Path(temp_path).unlink(missing_ok=True)


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
            def __init__(self, service_b: "ServiceB"):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a

        container.register_singleton(ServiceA, ServiceA)
        container.register_singleton(ServiceB, ServiceB)

        # This should raise an error due to circular dependency
        with pytest.raises((ValueError, RecursionError)):
            container.resolve(ServiceA)

    def test_container_with_invalid_service_registration(self):
        """Test container with invalid service registration."""
        from src.infrastructure.container import DependencyContainer

        container = DependencyContainer()

        # Register with invalid parameters
        with pytest.raises(TypeError):
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
            )

            # Create large dataset
            param_id = ParameterId("stress_test_param", "NYC")
            start_date = date(2000, 1, 1)

            # Create 10,000 data points (about 27 years of daily data)
            data_points = [
                DataPoint(start_date + timedelta(days=i), float(i % 100))
                for i in range(10000)
            ]

            historical_data = HistoricalData(param_id, data_points)

            # This should handle large datasets
            repo.save_historical_data(historical_data)

            # Verify data can be retrieved
            retrieved_data = repo.get_historical_data(
                param_id.parameter_name,
                param_id.geographic_code,
                start_date,
                start_date + timedelta(days=9999),
            )

            assert retrieved_data is not None
            assert len(retrieved_data.data_points) == 10000

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_simulation_repository_with_corrupted_json_data(self):
        """Test simulation repository with corrupted JSON data."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_path = temp_db.name

        try:
            repo = SQLiteSimulationRepository(temp_path)
            repo._init_database()

            # Manually insert corrupted JSON data
            import sqlite3

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO simulation_results 
                (simulation_id, property_id, msa_code, simulation_date, scenarios_json, correlation_matrix_json, summary_stats_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    "test_sim_1",
                    "test_prop_1",
                    "NYC",
                    "2023-01-01 12:00:00",
                    "invalid json data",  # Corrupted JSON
                    "{}",
                    "{}",
                ),
            )

            conn.commit()
            conn.close()

            # Repository should handle corrupted data gracefully
            result = repo.get_simulation_result("test_sim_1")
            assert result is None  # Should return None for corrupted data

        finally:
            Path(temp_path).unlink(missing_ok=True)

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
            )

            # Create valid data
            param_id = ParameterId("test_param", "NYC")
            data_points = [DataPoint(date(2023, 1, 1), 1.0)]
            historical_data = HistoricalData(param_id, data_points)

            # Mock a database error during save
            with patch.object(repo, "_get_connection") as mock_get_conn:
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.execute.side_effect = sqlite3.OperationalError(
                    "Simulated error"
                )
                mock_conn.cursor.return_value = mock_cursor
                mock_get_conn.return_value = mock_conn

                with pytest.raises(DatabaseError):
                    repo.save_historical_data(historical_data)

                # Verify rollback was called
                mock_conn.rollback.assert_called_once()

        finally:
            Path(temp_path).unlink(missing_ok=True)
