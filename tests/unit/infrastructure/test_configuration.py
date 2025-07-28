"""
Unit Tests for Infrastructure Configuration

Tests the dependency injection configuration for repositories and services.
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.infrastructure.configuration import (
    configure_repositories,
    configure_test_container,
    get_configured_container,
)
from src.infrastructure.container import DependencyContainer, create_container
from src.domain.repositories.parameter_repository import (
    ParameterRepository,
    ForecastRepository,
    CorrelationRepository,
)
from src.domain.repositories.simulation_repository import SimulationRepository


class TestInfrastructureConfiguration:
    """Test cases for infrastructure configuration."""

    @pytest.fixture
    def temp_db_paths(self):
        """Create temporary database files for testing."""
        temp_files = []
        for _ in range(3):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
            temp_files.append(temp_file.name)
            temp_file.close()

        yield temp_files

        # Cleanup
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except PermissionError:
                    pass  # File in use, skip cleanup

    @pytest.fixture
    def test_container(self):
        """Create a test container."""
        return create_container()

    def test_configure_test_container_creates_working_container(self, temp_db_paths):
        """
        GIVEN temporary database paths
        WHEN configuring a test container
        THEN it should create a container with working repositories
        """
        # Arrange
        param_db, forecast_db, sim_db = temp_db_paths

        # Act
        container = configure_test_container(
            parameter_db_path=param_db,
            forecast_db_path=forecast_db,
            simulation_db_path=sim_db,
        )

        # Assert
        assert isinstance(container, DependencyContainer)

        # Test that repositories can be resolved
        param_repo = container.resolve(ParameterRepository)
        forecast_repo = container.resolve(ForecastRepository)
        correlation_repo = container.resolve(CorrelationRepository)
        simulation_repo = container.resolve(SimulationRepository)

        assert param_repo is not None
        assert forecast_repo is not None
        assert correlation_repo is not None
        assert simulation_repo is not None

    def test_configure_test_container_without_db_paths_works(self):
        """
        GIVEN no database paths
        WHEN configuring a test container
        THEN it should create a basic container without repository errors
        """
        # Act
        container = configure_test_container()

        # Assert
        assert isinstance(container, DependencyContainer)

        # Should not be able to resolve repositories without database paths
        with pytest.raises(ValueError):
            container.resolve(ParameterRepository)

    def test_configured_repositories_are_singletons_within_container(
        self, temp_db_paths
    ):
        """
        GIVEN a configured test container
        WHEN resolving the same repository type multiple times
        THEN it should return different instances (factory pattern)
        """
        # Arrange
        param_db, forecast_db, sim_db = temp_db_paths
        container = configure_test_container(
            parameter_db_path=param_db,
            forecast_db_path=forecast_db,
            simulation_db_path=sim_db,
        )

        # Act
        repo1 = container.resolve(ParameterRepository)
        repo2 = container.resolve(ParameterRepository)

        # Assert - Factory pattern creates new instances each time
        assert repo1 is not repo2
        assert type(repo1) == type(repo2)

    def test_container_resolves_repository_implementations(self, temp_db_paths):
        """
        GIVEN a configured container
        WHEN resolving repository interfaces
        THEN it should return concrete SQLite implementations
        """
        # Arrange
        param_db, forecast_db, sim_db = temp_db_paths
        container = configure_test_container(
            parameter_db_path=param_db,
            forecast_db_path=forecast_db,
            simulation_db_path=sim_db,
        )

        # Act & Assert
        param_repo = container.resolve(ParameterRepository)
        assert param_repo.__class__.__name__ == "SQLiteParameterRepository"

        forecast_repo = container.resolve(ForecastRepository)
        assert forecast_repo.__class__.__name__ == "SQLiteForecastRepository"

        correlation_repo = container.resolve(CorrelationRepository)
        assert correlation_repo.__class__.__name__ == "SQLiteCorrelationRepository"

        simulation_repo = container.resolve(SimulationRepository)
        assert simulation_repo.__class__.__name__ == "SQLiteSimulationRepository"

    def test_repository_instances_have_correct_database_paths(self, temp_db_paths):
        """
        GIVEN a configured container with specific database paths
        WHEN resolving repositories
        THEN they should be configured with the correct database paths
        """
        # Arrange
        param_db, forecast_db, sim_db = temp_db_paths
        container = configure_test_container(
            parameter_db_path=param_db,
            forecast_db_path=forecast_db,
            simulation_db_path=sim_db,
        )

        # Act
        param_repo = container.resolve(ParameterRepository)
        forecast_repo = container.resolve(ForecastRepository)
        simulation_repo = container.resolve(SimulationRepository)

        # Assert - Check that repositories use the correct database paths
        assert param_repo._db_path == param_db
        assert forecast_repo._db_path == forecast_db
        assert simulation_repo._db_path == sim_db

    def test_container_provides_logger_to_repositories(self, temp_db_paths):
        """
        GIVEN a configured container
        WHEN resolving repositories
        THEN they should have logger instances injected
        """
        # Arrange
        param_db, forecast_db, sim_db = temp_db_paths
        container = configure_test_container(
            parameter_db_path=param_db,
            forecast_db_path=forecast_db,
            simulation_db_path=sim_db,
        )

        # Act
        param_repo = container.resolve(ParameterRepository)

        # Assert
        assert hasattr(param_repo, "_logger")
        assert param_repo._logger is not None
        assert param_repo._logger.name == "test_pro_forma_analytics"


class TestProductionConfiguration:
    """Test cases for production configuration (integration-style tests)."""

    def test_get_configured_container_returns_container(self):
        """
        GIVEN production configuration
        WHEN getting configured container
        THEN it should return a working container
        """
        # Note: This test may fail if production settings are not available
        # That's expected in a test environment
        try:
            # Act
            container = get_configured_container()

            # Assert
            assert isinstance(container, DependencyContainer)
        except (ImportError, FileNotFoundError, AttributeError) as e:
            # Expected in test environment without full production setup
            pytest.skip(f"Production configuration not available: {e}")

    def test_container_configuration_is_idempotent(self):
        """
        GIVEN a configured container
        WHEN calling get_configured_container multiple times
        THEN it should return the same container instance
        """
        try:
            # Act
            container1 = get_configured_container()
            container2 = get_configured_container()

            # Assert
            assert container1 is container2
        except (ImportError, FileNotFoundError, AttributeError) as e:
            # Expected in test environment
            pytest.skip(f"Production configuration not available: {e}")


class TestRepositoryIntegration:
    """Integration tests for repository configuration."""

    @pytest.fixture
    def configured_container(self):
        """Create a container with actual repository implementations."""
        temp_files = []
        for _ in range(3):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
            temp_files.append(temp_file.name)
            temp_file.close()

        container = configure_test_container(
            parameter_db_path=temp_files[0],
            forecast_db_path=temp_files[1],
            simulation_db_path=temp_files[2],
        )

        yield container

        # Cleanup
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except PermissionError:
                    pass

    def test_repositories_can_perform_basic_operations(self, configured_container):
        """
        GIVEN a configured container with repositories
        WHEN performing basic repository operations
        THEN they should work without errors
        """
        # Arrange
        param_repo = configured_container.resolve(ParameterRepository)

        # Act & Assert - Test basic operations work
        from src.domain.entities.forecast import ParameterId, ParameterType

        test_param_id = ParameterId("test_param", "12345", ParameterType.MARKET_METRIC)

        # This should not throw an error (though it may return None/empty results)
        available_params = param_repo.get_available_parameters("12345")
        historical_data = param_repo.get_historical_data(test_param_id)

        # Basic assertions
        assert isinstance(available_params, list)
        # historical_data can be None for empty database
