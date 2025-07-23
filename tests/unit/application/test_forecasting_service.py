"""
Unit Tests for Forecasting Application Service

Tests the application service layer following BDD/TDD principles.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime

from src.application.services.forecasting_service import (
    ForecastingApplicationService,
    ForecastError,
    DataNotFoundError
)
from src.domain.entities.forecast import (
    ParameterId,
    ParameterType,
    ForecastRequest,
    ForecastResult,
    DataPoint,
    HistoricalData
)


class TestForecastingApplicationService:
    """Test cases for ForecastingApplicationService."""
    
    def test_generate_forecast_with_cached_forecast_should_return_cached_result(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_parameter_id,
        sample_forecast_result
    ):
        """
        GIVEN a cached forecast exists
        WHEN generating a forecast
        THEN it should return the cached result without calling the engine
        """
        # Arrange
        mock_forecast_repository.get_cached_forecast.return_value = sample_forecast_result
        
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        request = ForecastRequest(
            parameter_id=sample_parameter_id,
            horizon_years=1,
            model_type="prophet"
        )
        
        # Act
        result = service.generate_forecast(request)
        
        # Assert
        assert result == sample_forecast_result
        mock_forecast_repository.get_cached_forecast.assert_called_once()
        mock_forecasting_engine.generate_forecast.assert_not_called()
        mock_parameter_repository.get_historical_data.assert_not_called()
    
    def test_generate_forecast_without_cached_forecast_should_create_new_forecast(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_parameter_id,
        sample_historical_data,
        sample_forecast_result
    ):
        """
        GIVEN no cached forecast exists
        WHEN generating a forecast
        THEN it should load historical data, generate new forecast, and cache result
        """
        # Arrange
        mock_forecast_repository.get_cached_forecast.return_value = None
        mock_parameter_repository.get_historical_data.return_value = sample_historical_data
        mock_forecasting_engine.generate_forecast.return_value = sample_forecast_result
        
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        request = ForecastRequest(
            parameter_id=sample_parameter_id,
            horizon_years=1,
            model_type="prophet"
        )
        
        # Act
        result = service.generate_forecast(request)
        
        # Assert
        assert result == sample_forecast_result
        mock_forecast_repository.get_cached_forecast.assert_called_once()
        mock_parameter_repository.get_historical_data.assert_called_once_with(sample_parameter_id)
        mock_forecasting_engine.generate_forecast.assert_called_once_with(request, sample_historical_data)
        mock_forecast_repository.save_forecast.assert_called_once_with(sample_forecast_result)
    
    def test_generate_forecast_with_no_historical_data_should_raise_data_not_found_error(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_parameter_id
    ):
        """
        GIVEN no historical data exists
        WHEN generating a forecast
        THEN it should raise DataNotFoundError
        """
        # Arrange
        mock_forecast_repository.get_cached_forecast.return_value = None
        mock_parameter_repository.get_historical_data.return_value = None
        
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        request = ForecastRequest(
            parameter_id=sample_parameter_id,
            horizon_years=1,
            model_type="prophet"
        )
        
        # Act & Assert
        with pytest.raises(DataNotFoundError, match="No historical data found"):
            service.generate_forecast(request)
        
        mock_forecasting_engine.generate_forecast.assert_not_called()
        mock_forecast_repository.save_forecast.assert_not_called()
    
    def test_generate_forecast_with_insufficient_historical_data_should_raise_data_not_found_error(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_parameter_id
    ):
        """
        GIVEN insufficient historical data (< 24 points)
        WHEN generating a forecast
        THEN it should raise DataNotFoundError
        """
        # Arrange
        mock_forecast_repository.get_cached_forecast.return_value = None
        
        # Create historical data with insufficient points
        data_points = [
            DataPoint(sample_parameter_id, date(2023, 1, 1), 0.05, "test")
            for _ in range(10)  # Only 10 points, need 24
        ]
        insufficient_data = HistoricalData(
            parameter_id=sample_parameter_id,
            data_points=data_points,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 10, 1)
        )
        
        mock_parameter_repository.get_historical_data.return_value = insufficient_data
        
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        request = ForecastRequest(
            parameter_id=sample_parameter_id,
            horizon_years=1,
            model_type="prophet"
        )
        
        # Act & Assert
        with pytest.raises(DataNotFoundError, match="Insufficient historical data"):
            service.generate_forecast(request)
        
        mock_forecasting_engine.generate_forecast.assert_not_called()
    
    def test_generate_forecast_when_forecasting_engine_fails_should_raise_forecast_error(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_parameter_id,
        sample_historical_data
    ):
        """
        GIVEN forecasting engine raises exception
        WHEN generating a forecast
        THEN it should raise ForecastError
        """
        # Arrange
        mock_forecast_repository.get_cached_forecast.return_value = None
        mock_parameter_repository.get_historical_data.return_value = sample_historical_data
        mock_forecasting_engine.generate_forecast.side_effect = Exception("Engine failed")
        
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        request = ForecastRequest(
            parameter_id=sample_parameter_id,
            horizon_years=1,
            model_type="prophet"
        )
        
        # Act & Assert
        with pytest.raises(ForecastError, match="Failed to generate forecast"):
            service.generate_forecast(request)
        
        mock_forecast_repository.save_forecast.assert_not_called()
    
    def test_generate_multiple_forecasts_should_return_results_for_all_parameters(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_historical_data,
        sample_forecast_result
    ):
        """
        GIVEN multiple parameter IDs
        WHEN generating multiple forecasts
        THEN it should return forecast results for all parameters
        """
        # Arrange
        parameter_ids = [
            ParameterId("cap_rate", "35620", ParameterType.MARKET_METRIC),
            ParameterId("vacancy_rate", "35620", ParameterType.MARKET_METRIC),
            ParameterId("rent_growth", "35620", ParameterType.GROWTH_METRIC)
        ]
        
        # Mock no cached forecasts
        mock_forecast_repository.get_forecasts_for_simulation.return_value = {}
        mock_forecast_repository.get_cached_forecast.return_value = None
        
        # Mock historical data and forecast generation
        mock_parameter_repository.get_historical_data.return_value = sample_historical_data
        mock_forecasting_engine.generate_forecast.return_value = sample_forecast_result
        
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        # Act
        results = service.generate_multiple_forecasts(
            parameter_ids=parameter_ids,
            horizon_years=5,
            model_type="prophet"
        )
        
        # Assert
        assert len(results) == 3
        assert all(param_id in results for param_id in parameter_ids)
        assert mock_forecasting_engine.generate_forecast.call_count == 3
    
    def test_validate_forecast_quality_with_good_forecast_should_return_true(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_forecast_result
    ):
        """
        GIVEN a high-quality forecast
        WHEN validating forecast quality
        THEN it should return True
        """
        # Arrange
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        # Act
        is_valid = service.validate_forecast_quality(sample_forecast_result)
        
        # Assert
        assert is_valid is True
    
    def test_validate_forecast_quality_with_poor_forecast_should_return_false(
        self,
        mock_parameter_repository,
        mock_forecast_repository,
        mock_forecasting_engine,
        sample_forecast_result
    ):
        """
        GIVEN a poor-quality forecast
        WHEN validating forecast quality
        THEN it should return False
        """
        # Arrange
        service = ForecastingApplicationService(
            parameter_repository=mock_parameter_repository,
            forecast_repository=mock_forecast_repository,
            forecasting_engine=mock_forecasting_engine
        )
        
        # Set strict quality thresholds that the sample won't meet
        strict_thresholds = {
            'mae': 0.001,  # Very strict
            'mape': 1.0,   # Very strict
            'rmse': 0.001, # Very strict
            'r_squared': 0.99  # Very strict
        }
        
        # Act
        is_valid = service.validate_forecast_quality(
            sample_forecast_result,
            strict_thresholds
        )
        
        # Assert
        assert is_valid is False