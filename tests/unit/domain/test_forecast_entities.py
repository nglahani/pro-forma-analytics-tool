"""
Unit Tests for Forecast Domain Entities

Tests the core business entities following TDD/BDD principles.
"""

from datetime import date

import pytest

from src.domain.entities.forecast import (
    DataPoint,
    ForecastRequest,
    HistoricalData,
    ModelPerformance,
    ParameterId,
    ParameterType,
)


class TestParameterId:
    """Test cases for ParameterId value object."""

    def test_parameter_id_creation_with_valid_data_should_succeed(self):
        """GIVEN valid parameter data WHEN creating ParameterId THEN it should succeed."""
        # Arrange
        name = "cap_rate"
        geographic_code = "35620"
        parameter_type = ParameterType.MARKET_METRIC

        # Act
        parameter_id = ParameterId(
            name=name, geographic_code=geographic_code, parameter_type=parameter_type
        )

        # Assert
        assert parameter_id.name == name
        assert parameter_id.geographic_code == geographic_code
        assert parameter_id.parameter_type == parameter_type

    def test_parameter_id_creation_with_empty_name_should_raise_error(self):
        """GIVEN empty parameter name WHEN creating ParameterId THEN it should raise ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Parameter name and geographic code are required"
        ):
            ParameterId(
                name="",
                geographic_code="35620",
                parameter_type=ParameterType.MARKET_METRIC,
            )

    def test_parameter_id_creation_with_empty_geographic_code_should_raise_error(self):
        """GIVEN empty geographic code WHEN creating ParameterId THEN it should raise ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Parameter name and geographic code are required"
        ):
            ParameterId(
                name="cap_rate",
                geographic_code="",
                parameter_type=ParameterType.MARKET_METRIC,
            )

    def test_parameter_id_immutability(self):
        """GIVEN a ParameterId WHEN trying to modify it THEN it should be immutable."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Act & Assert
        with pytest.raises(AttributeError):
            parameter_id.name = "new_name"


class TestDataPoint:
    """Test cases for DataPoint entity."""

    def test_data_point_creation_with_valid_data_should_succeed(self):
        """GIVEN valid data point data WHEN creating DataPoint THEN it should succeed."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Act
        data_point = DataPoint(
            parameter_id=parameter_id,
            date=date(2023, 1, 1),
            value=0.05,
            data_source="test",
        )

        # Assert
        assert data_point.parameter_id == parameter_id
        assert data_point.date == date(2023, 1, 1)
        assert data_point.value == 0.05
        assert data_point.data_source == "test"

    def test_data_point_creation_with_none_value_should_raise_error(self):
        """GIVEN None value WHEN creating DataPoint THEN it should raise ValueError."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Data point value cannot be None"):
            DataPoint(
                parameter_id=parameter_id,
                date=date(2023, 1, 1),
                value=None,
                data_source="test",
            )


class TestHistoricalData:
    """Test cases for HistoricalData entity."""

    def test_historical_data_creation_with_valid_data_should_succeed(self):
        """GIVEN valid historical data WHEN creating HistoricalData THEN it should succeed."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        data_points = [
            DataPoint(parameter_id, date(2023, 1, 1), 0.05, "test"),
            DataPoint(parameter_id, date(2023, 2, 1), 0.051, "test"),
            DataPoint(parameter_id, date(2023, 3, 1), 0.052, "test"),
        ]

        # Act
        historical_data = HistoricalData(
            parameter_id=parameter_id,
            data_points=data_points,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 3, 1),
        )

        # Assert
        assert historical_data.parameter_id == parameter_id
        assert len(historical_data.data_points) == 3
        assert historical_data.start_date == date(2023, 1, 1)
        assert historical_data.end_date == date(2023, 3, 1)

    def test_historical_data_values_property_should_return_ordered_values(self):
        """GIVEN historical data WHEN accessing values property THEN it should return ordered values."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Create data points out of order
        data_points = [
            DataPoint(parameter_id, date(2023, 3, 1), 0.052, "test"),
            DataPoint(parameter_id, date(2023, 1, 1), 0.05, "test"),
            DataPoint(parameter_id, date(2023, 2, 1), 0.051, "test"),
        ]

        historical_data = HistoricalData(
            parameter_id=parameter_id,
            data_points=data_points,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 3, 1),
        )

        # Act
        values = historical_data.values

        # Assert
        assert values == [0.05, 0.051, 0.052]  # Should be ordered by date

    def test_historical_data_with_empty_data_points_should_raise_error(self):
        """GIVEN empty data points WHEN creating HistoricalData THEN it should raise ValueError."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Act & Assert
        with pytest.raises(
            ValueError, match="Historical data must contain at least one data point"
        ):
            HistoricalData(
                parameter_id=parameter_id,
                data_points=[],
                start_date=date(2023, 1, 1),
                end_date=date(2023, 3, 1),
            )

    def test_historical_data_with_inconsistent_date_range_should_raise_error(self):
        """GIVEN inconsistent date range WHEN creating HistoricalData THEN it should raise ValueError."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        data_points = [
            DataPoint(parameter_id, date(2023, 1, 1), 0.05, "test"),
            DataPoint(parameter_id, date(2023, 2, 1), 0.051, "test"),
        ]

        # Act & Assert
        with pytest.raises(
            ValueError, match="Date range does not match actual data points"
        ):
            HistoricalData(
                parameter_id=parameter_id,
                data_points=data_points,
                start_date=date(2022, 12, 1),  # Wrong start date
                end_date=date(2023, 2, 1),
            )


class TestModelPerformance:
    """Test cases for ModelPerformance entity."""

    def test_model_performance_is_acceptable_with_good_metrics_should_return_true(self):
        """GIVEN good performance metrics WHEN checking acceptability THEN it should return True."""
        # Arrange
        performance = ModelPerformance(mae=0.005, mape=5.0, rmse=0.008, r_squared=0.95)

        thresholds = {"mae": 0.01, "mape": 10.0, "rmse": 0.01, "r_squared": 0.9}

        # Act
        is_acceptable = performance.is_acceptable(thresholds)

        # Assert
        assert is_acceptable is True

    def test_model_performance_is_acceptable_with_poor_metrics_should_return_false(
        self,
    ):
        """GIVEN poor performance metrics WHEN checking acceptability THEN it should return False."""
        # Arrange
        performance = ModelPerformance(
            mae=0.05,  # Too high
            mape=25.0,  # Too high
            rmse=0.08,  # Too high
            r_squared=0.5,  # Too low
        )

        thresholds = {"mae": 0.01, "mape": 10.0, "rmse": 0.01, "r_squared": 0.9}

        # Act
        is_acceptable = performance.is_acceptable(thresholds)

        # Assert
        assert is_acceptable is False


class TestForecastRequest:
    """Test cases for ForecastRequest entity."""

    def test_forecast_request_creation_with_valid_data_should_succeed(self):
        """GIVEN valid request data WHEN creating ForecastRequest THEN it should succeed."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Act
        request = ForecastRequest(
            parameter_id=parameter_id,
            horizon_years=5,
            model_type="prophet",
            confidence_level=0.95,
        )

        # Assert
        assert request.parameter_id == parameter_id
        assert request.horizon_years == 5
        assert request.model_type == "prophet"
        assert request.confidence_level == 0.95

    def test_forecast_request_with_zero_horizon_should_raise_error(self):
        """GIVEN zero horizon years WHEN creating ForecastRequest THEN it should raise ValueError."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Forecast horizon must be positive"):
            ForecastRequest(
                parameter_id=parameter_id, horizon_years=0, model_type="prophet"
            )

    def test_forecast_request_with_invalid_confidence_level_should_raise_error(self):
        """GIVEN invalid confidence level WHEN creating ForecastRequest THEN it should raise ValueError."""
        # Arrange
        parameter_id = ParameterId(
            name="cap_rate",
            geographic_code="35620",
            parameter_type=ParameterType.MARKET_METRIC,
        )

        # Act & Assert
        with pytest.raises(
            ValueError, match="Confidence level must be between 0 and 1"
        ):
            ForecastRequest(
                parameter_id=parameter_id,
                horizon_years=5,
                model_type="prophet",
                confidence_level=1.5,  # Invalid
            )
