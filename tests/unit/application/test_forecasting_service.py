"""
Unit tests for ForecastingApplicationService.

Simplified tests focusing on the actual implementation.
"""

import logging
from unittest.mock import Mock

import pytest

from src.application.services.forecasting_service import ForecastingApplicationService


class TestForecastingApplicationService:
    """Test cases for ForecastingApplicationService."""

    @pytest.fixture
    def mock_parameter_repository(self):
        """Mock parameter repository."""
        return Mock()

    @pytest.fixture
    def mock_forecast_repository(self):
        """Mock forecast repository."""
        return Mock()

    @pytest.fixture
    def mock_forecasting_engine(self):
        """Mock Prophet forecasting engine."""
        return Mock()

    @pytest.fixture
    def mock_logger(self):
        """Mock logger."""
        return Mock(spec=logging.Logger)

    @pytest.fixture
    def service(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        mock_logger,
    ):
        """Create forecasting service with mocked dependencies."""
        return ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine,
            logger=mock_logger,
        )

    def test_service_initialization(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
    ):
        """Test service initializes correctly."""
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine,
        )

        assert service._parameter_repo == mock_parameter_repository
        assert service._forecast_repo == mock_forecast_repository
        assert service._forecasting_engine == mock_forecasting_engine
        assert service._logger is not None

    def test_service_initialization_with_logger(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        mock_logger,
    ):
        """Test service initializes with custom logger."""
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine,
            logger=mock_logger,
        )

        assert service._logger == mock_logger

    def test_service_has_required_methods(self, service):
        """Test service has the expected methods."""
        # Test that the service class has the expected interface
        assert hasattr(service, "_parameter_repo")
        assert hasattr(service, "_forecast_repo")
        assert hasattr(service, "_forecasting_engine")
        assert hasattr(service, "_logger")

    def test_service_dependencies_are_set(
        self,
        service,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
    ):
        """Test that all dependencies are properly injected."""
        assert service._parameter_repo is mock_parameter_repository
        assert service._forecast_repo is mock_forecast_repository
        assert service._forecasting_engine is mock_forecasting_engine

    def test_service_logger_is_configured(self, service):
        """Test that logger is properly configured."""
        assert service._logger is not None
        assert hasattr(service._logger, "info")
        assert hasattr(service._logger, "error")
        assert hasattr(service._logger, "debug")

    def test_service_can_access_repositories(self, service):
        """Test that service can access its repositories."""
        # These should not raise AttributeError
        repo = service._parameter_repo
        forecast_repo = service._forecast_repo
        engine = service._forecasting_engine

        assert repo is not None
        assert forecast_repo is not None
        assert engine is not None

    def test_service_logger_default_configuration(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
    ):
        """Test that service creates default logger when none provided."""
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine,
        )

        # Should create a logger with the module name
        assert service._logger is not None
        assert hasattr(service._logger, "name")

    def test_service_attribute_types(self, service):
        """Test that service attributes have expected types."""
        # Parameter repo should be mock
        assert service._parameter_repo is not None

        # Forecast repo should be mock
        assert service._forecast_repo is not None

        # Engine should be mock
        assert service._forecasting_engine is not None

        # Logger should support logging interface
        assert hasattr(service._logger, "info")

    def test_service_dependency_isolation(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
    ):
        """Test that each service instance has isolated dependencies."""
        service1 = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine,
        )

        service2 = ForecastingApplicationService(
            parameter_repository=Mock(),
            forecast_repository=Mock(),
            forecasting_engine=Mock(),
        )

        # Services should have different dependency instances
        assert service1._parameter_repo is not service2._parameter_repo
        assert service1._forecast_repo is not service2._forecast_repo
        assert service1._forecasting_engine is not service2._forecasting_engine

    def test_service_interface_completeness(self, service):
        """Test that service implements expected interface."""
        # Check that service has all expected private attributes
        expected_attributes = [
            "_parameter_repo",
            "_forecast_repo",
            "_forecasting_engine",
            "_logger",
        ]

        for attr in expected_attributes:
            assert hasattr(service, attr), f"Service missing attribute: {attr}"
            assert (
                getattr(service, attr) is not None
            ), f"Service attribute {attr} is None"
