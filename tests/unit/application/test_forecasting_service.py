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

    def test_generate_forecast_with_cached_result(self, service):
        """Test generate_forecast returns cached result when available."""
        from src.domain.entities.forecast import (
            ForecastRequest,
            ForecastResult,
            ParameterId,
            ParameterType,
        )

        # Setup mocks
        parameter_id = ParameterId(
            name="interest_rate",
            geographic_code="NYC",
            parameter_type=ParameterType.INTEREST_RATE,
        )
        request = ForecastRequest(
            parameter_id=parameter_id,
            horizon_years=5,
            model_type="prophet",
            confidence_level=0.95,
        )

        cached_result = Mock(spec=ForecastResult)
        service._forecast_repo.get_cached_forecast.return_value = cached_result

        # Execute
        result = service.generate_forecast(request)

        # Verify
        assert result == cached_result
        service._forecast_repo.get_cached_forecast.assert_called_once()
        service._parameter_repo.get_historical_data.assert_not_called()
        service._forecasting_engine.generate_forecast.assert_not_called()

    def test_generate_forecast_with_no_cache(self, service):
        """Test generate_forecast generates new forecast when no cache exists."""
        from src.domain.entities.forecast import (
            DataPoint,
            ForecastRequest,
            HistoricalData,
            ParameterId,
            ParameterType,
        )

        # Setup mocks
        parameter_id = ParameterId(
            name="interest_rate",
            geographic_code="NYC",
            parameter_type=ParameterType.INTEREST_RATE,
        )
        request = ForecastRequest(
            parameter_id=parameter_id,
            horizon_years=5,
            model_type="prophet",
            confidence_level=0.95,
        )

        # Mock historical data with sufficient points
        data_points = [Mock(spec=DataPoint) for _ in range(30)]
        historical_data = Mock(spec=HistoricalData)
        historical_data.data_points = data_points

        service._forecast_repo.get_cached_forecast.return_value = None
        service._parameter_repo.get_historical_data.return_value = historical_data

        forecast_result = Mock()
        service._forecasting_engine.generate_forecast.return_value = forecast_result

        # Execute
        result = service.generate_forecast(request)

        # Verify
        assert result == forecast_result
        service._forecast_repo.get_cached_forecast.assert_called_once()
        service._parameter_repo.get_historical_data.assert_called_once_with(
            parameter_id
        )
        service._forecasting_engine.generate_forecast.assert_called_once_with(
            request, historical_data
        )
        service._forecast_repo.save_forecast.assert_called_once_with(forecast_result)

    def test_generate_forecast_no_historical_data(self, service):
        """Test generate_forecast raises error when no historical data exists."""
        from core.exceptions import DataNotFoundError
        from src.domain.entities.forecast import (
            ForecastRequest,
            ParameterId,
            ParameterType,
        )

        # Setup mocks
        parameter_id = ParameterId(
            name="interest_rate",
            geographic_code="NYC",
            parameter_type=ParameterType.INTEREST_RATE,
        )
        request = ForecastRequest(
            parameter_id=parameter_id,
            horizon_years=5,
            model_type="prophet",
            confidence_level=0.95,
        )

        service._forecast_repo.get_cached_forecast.return_value = None
        service._parameter_repo.get_historical_data.return_value = None

        # Execute & Verify
        with pytest.raises(DataNotFoundError, match="No historical data found"):
            service.generate_forecast(request)

    def test_generate_forecast_insufficient_historical_data(self, service):
        """Test generate_forecast raises error when historical data is insufficient."""
        from core.exceptions import DataNotFoundError
        from src.domain.entities.forecast import (
            DataPoint,
            ForecastRequest,
            HistoricalData,
            ParameterId,
            ParameterType,
        )

        # Setup mocks
        parameter_id = ParameterId(
            name="interest_rate",
            geographic_code="NYC",
            parameter_type=ParameterType.INTEREST_RATE,
        )
        request = ForecastRequest(
            parameter_id=parameter_id,
            horizon_years=5,
            model_type="prophet",
            confidence_level=0.95,
        )

        # Mock insufficient historical data (< 24 points)
        data_points = [Mock(spec=DataPoint) for _ in range(12)]
        historical_data = Mock(spec=HistoricalData)
        historical_data.data_points = data_points

        service._forecast_repo.get_cached_forecast.return_value = None
        service._parameter_repo.get_historical_data.return_value = historical_data

        # Execute & Verify
        with pytest.raises(DataNotFoundError, match="Insufficient historical data"):
            service.generate_forecast(request)

    def test_generate_forecast_engine_failure(self, service):
        """Test generate_forecast handles engine failures gracefully."""
        from core.exceptions import ForecastError
        from src.domain.entities.forecast import (
            DataPoint,
            ForecastRequest,
            HistoricalData,
            ParameterId,
            ParameterType,
        )

        # Setup mocks
        parameter_id = ParameterId(
            name="interest_rate",
            geographic_code="NYC",
            parameter_type=ParameterType.INTEREST_RATE,
        )
        request = ForecastRequest(
            parameter_id=parameter_id,
            horizon_years=5,
            model_type="prophet",
            confidence_level=0.95,
        )

        data_points = [Mock(spec=DataPoint) for _ in range(30)]
        historical_data = Mock(spec=HistoricalData)
        historical_data.data_points = data_points

        service._forecast_repo.get_cached_forecast.return_value = None
        service._parameter_repo.get_historical_data.return_value = historical_data
        service._forecasting_engine.generate_forecast.side_effect = Exception(
            "Engine failed"
        )

        # Execute & Verify
        with pytest.raises(ForecastError, match="Failed to generate forecast"):
            service.generate_forecast(request)

    def test_generate_multiple_forecasts_success(self, service):
        """Test generate_multiple_forecasts successfully processes multiple parameters."""
        from src.domain.entities.forecast import (
            ForecastResult,
            ParameterId,
            ParameterType,
        )

        # Setup
        param_ids = [
            ParameterId(
                name="interest_rate",
                geographic_code="NYC",
                parameter_type=ParameterType.INTEREST_RATE,
            ),
            ParameterId(
                name="cap_rate",
                geographic_code="LA",
                parameter_type=ParameterType.MARKET_METRIC,
            ),
        ]

        service._forecast_repo.get_forecasts_for_simulation.return_value = {}

        # Mock successful forecast generation
        forecast_results = {
            param_ids[0]: Mock(spec=ForecastResult),
            param_ids[1]: Mock(spec=ForecastResult),
        }

        service.generate_forecast = Mock(
            side_effect=lambda req: forecast_results[req.parameter_id]
        )

        # Execute
        results = service.generate_multiple_forecasts(param_ids, 5)

        # Verify
        assert len(results) == 2
        assert param_ids[0] in results
        assert param_ids[1] in results

    def test_generate_multiple_forecasts_with_cached(self, service):
        """Test generate_multiple_forecasts uses cached results when available."""
        from src.domain.entities.forecast import (
            ForecastResult,
            ParameterId,
            ParameterType,
        )

        # Setup
        param_ids = [
            ParameterId(
                name="interest_rate",
                geographic_code="NYC",
                parameter_type=ParameterType.INTEREST_RATE,
            ),
            ParameterId(
                name="cap_rate",
                geographic_code="LA",
                parameter_type=ParameterType.MARKET_METRIC,
            ),
        ]

        cached_result = Mock(spec=ForecastResult)
        service._forecast_repo.get_forecasts_for_simulation.return_value = {
            param_ids[0]: cached_result
        }

        new_result = Mock(spec=ForecastResult)
        service.generate_forecast = Mock(return_value=new_result)

        # Execute
        results = service.generate_multiple_forecasts(param_ids, 5)

        # Verify
        assert results[param_ids[0]] == cached_result  # Cached
        assert results[param_ids[1]] == new_result  # New
        service.generate_forecast.assert_called_once()

    def test_generate_multiple_forecasts_partial_failures(self, service):
        """Test generate_multiple_forecasts handles partial failures."""
        from src.domain.entities.forecast import (
            ForecastResult,
            ParameterId,
            ParameterType,
        )

        # Setup
        param_ids = [
            ParameterId(
                name="interest_rate",
                geographic_code="NYC",
                parameter_type=ParameterType.INTEREST_RATE,
            ),
            ParameterId(
                name="cap_rate",
                geographic_code="LA",
                parameter_type=ParameterType.MARKET_METRIC,
            ),
        ]

        service._forecast_repo.get_forecasts_for_simulation.return_value = {}

        success_result = Mock(spec=ForecastResult)

        def mock_generate_forecast(request):
            if request.parameter_id == param_ids[0]:
                return success_result
            else:
                raise Exception("Forecast failed")

        service.generate_forecast = Mock(side_effect=mock_generate_forecast)

        # Execute
        results = service.generate_multiple_forecasts(param_ids, 5)

        # Verify
        assert len(results) == 1
        assert results[param_ids[0]] == success_result

    def test_validate_forecast_quality_passes(self, service):
        """Test validate_forecast_quality returns True for good forecast."""
        from src.domain.entities.forecast import ForecastResult, ModelPerformance

        # Setup
        model_performance = Mock(spec=ModelPerformance)
        model_performance.is_acceptable.return_value = True

        forecast_result = Mock(spec=ForecastResult)
        forecast_result.model_performance = model_performance

        # Execute
        result = service.validate_forecast_quality(forecast_result)

        # Verify
        assert result is True
        model_performance.is_acceptable.assert_called_once()

    def test_validate_forecast_quality_fails(self, service):
        """Test validate_forecast_quality returns False for poor forecast."""
        from src.domain.entities.forecast import ForecastResult, ModelPerformance

        # Setup
        model_performance = Mock(spec=ModelPerformance)
        model_performance.is_acceptable.return_value = False
        model_performance.mae = 0.2
        model_performance.mape = 25.0
        model_performance.rmse = 0.3
        model_performance.r_squared = 0.5

        forecast_result = Mock(spec=ForecastResult)
        forecast_result.forecast_id = "test_forecast_123"
        forecast_result.model_performance = model_performance

        # Execute
        result = service.validate_forecast_quality(forecast_result)

        # Verify
        assert result is False

    def test_get_data_completeness_report_success(self, service):
        """Test get_data_completeness_report returns completeness percentages."""
        from datetime import date

        from src.domain.entities.forecast import ParameterId, ParameterType

        # Setup
        param_ids = [
            ParameterId(
                name="interest_rate",
                geographic_code="NYC",
                parameter_type=ParameterType.INTEREST_RATE,
            ),
            ParameterId(
                name="cap_rate",
                geographic_code="LA",
                parameter_type=ParameterType.MARKET_METRIC,
            ),
        ]

        service._parameter_repo.get_data_completeness.side_effect = [0.95, 0.87]

        # Execute
        start_date = date(2020, 1, 1)
        end_date = date(2023, 12, 31)
        report = service.get_data_completeness_report(param_ids, start_date, end_date)

        # Verify
        assert report[param_ids[0]] == 0.95
        assert report[param_ids[1]] == 0.87

    def test_get_data_completeness_report_with_errors(self, service):
        """Test get_data_completeness_report handles errors gracefully."""
        from datetime import date

        from src.domain.entities.forecast import ParameterId, ParameterType

        # Setup
        param_ids = [
            ParameterId(
                name="interest_rate",
                geographic_code="NYC",
                parameter_type=ParameterType.INTEREST_RATE,
            )
        ]
        service._parameter_repo.get_data_completeness.side_effect = Exception(
            "DB error"
        )

        # Execute
        start_date = date(2020, 1, 1)
        end_date = date(2023, 12, 31)
        report = service.get_data_completeness_report(param_ids, start_date, end_date)

        # Verify
        assert report[param_ids[0]] == 0.0
