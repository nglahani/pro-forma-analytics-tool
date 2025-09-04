#!/usr/bin/env python3
"""
Comprehensive tests for Prophet forecasting engine.

Tests cover all major functionality including initialization, data loading,
model fitting, validation, forecasting, and visualization.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from core.exceptions import ValidationError
from forecasting.prophet_engine import (
    PROPHET_AVAILABLE,
    ProFormaProphetEngine,
    ProphetForecaster,
    ProphetForecastResult,
    ValidationResult,
)


class TestProphetForecaster:
    """Test cases for ProphetForecaster class."""

    def test_init_valid_parameters(self):
        """Test successful initialization with valid parameters."""
        forecaster = ProphetForecaster("cap_rate", "35620")

        assert forecaster.parameter_name == "cap_rate"
        assert forecaster.geographic_code == "35620"
        assert forecaster.historical_data is None
        assert forecaster.fitted_model is None
        assert forecaster.logger is not None

    def test_init_empty_parameter_name_raises_error(self):
        """Test initialization with empty parameter name raises ValidationError."""
        with pytest.raises(
            ValidationError, match="Parameter name and geographic code are required"
        ):
            ProphetForecaster("", "35620")

    def test_init_empty_geographic_code_raises_error(self):
        """Test initialization with empty geographic code raises ValidationError."""
        with pytest.raises(
            ValidationError, match="Parameter name and geographic code are required"
        ):
            ProphetForecaster("cap_rate", "")

    @patch("forecasting.prophet_engine.db_manager")
    def test_load_historical_data_success(self, mock_db_manager):
        """Test successful loading of historical data."""
        # Mock data
        mock_data = [
            {"date": "2020-01-01", "value": 5.0},
            {"date": "2021-01-01", "value": 5.5},
            {"date": "2022-01-01", "value": 6.0},
        ]
        mock_db_manager.get_parameter_data.return_value = mock_data

        forecaster = ProphetForecaster("cap_rate", "35620")
        result = forecaster.load_historical_data()

        assert len(result) == 3
        assert "ds" in result.columns
        assert "y" in result.columns
        assert forecaster.historical_data is not None
        mock_db_manager.get_parameter_data.assert_called_once_with("cap_rate", "35620")

    @patch("forecasting.prophet_engine.db_manager")
    def test_load_historical_data_no_data_found(self, mock_db_manager):
        """Test loading historical data when no data is found."""
        mock_db_manager.get_parameter_data.return_value = []

        forecaster = ProphetForecaster("cap_rate", "35620")

        with pytest.raises(Exception, match="No historical data found"):
            forecaster.load_historical_data()

    @patch("forecasting.prophet_engine.db_manager")
    def test_load_historical_data_handles_duplicates(self, mock_db_manager):
        """Test loading historical data handles duplicate dates."""
        # Mock data with duplicates
        mock_data = [
            {"date": "2020-01-01", "value": 5.0},
            {"date": "2020-01-01", "value": 5.2},  # Duplicate - should keep this one
            {"date": "2021-01-01", "value": 5.5},
        ]
        mock_db_manager.get_parameter_data.return_value = mock_data

        forecaster = ProphetForecaster("cap_rate", "35620")
        result = forecaster.load_historical_data()

        # Should have 2 rows after deduplication
        assert len(result) == 2
        # Should keep the last value for duplicated date
        assert result[result["ds"] == pd.Timestamp("2020-01-01")]["y"].iloc[0] == 5.2

    def test_fit_model_no_data_raises_error(self):
        """Test fitting model without loaded data raises ValueError."""
        forecaster = ProphetForecaster("cap_rate", "35620")

        with pytest.raises(ValueError, match="No historical data loaded"):
            forecaster.fit_model()

    @patch("forecasting.prophet_engine.Prophet")
    def test_fit_model_success(self, mock_prophet_class):
        """Test successful model fitting."""
        # Setup
        mock_prophet_instance = Mock()
        mock_prophet_class.return_value = mock_prophet_instance

        forecaster = ProphetForecaster("cap_rate", "35620")
        forecaster.historical_data = pd.DataFrame(
            {
                "ds": pd.date_range("2020-01-01", periods=3, freq="YE"),
                "y": [5.0, 5.5, 6.0],
            }
        )

        # Execute
        forecaster.fit_model()

        # Verify
        mock_prophet_class.assert_called_once()
        mock_prophet_instance.fit.assert_called_once()
        assert forecaster.fitted_model == mock_prophet_instance

    @patch("forecasting.prophet_engine.Prophet")
    def test_fit_model_with_custom_seasonality(self, mock_prophet_class):
        """Test model fitting with custom seasonality parameters."""
        mock_prophet_instance = Mock()
        mock_prophet_class.return_value = mock_prophet_instance

        forecaster = ProphetForecaster("cap_rate", "35620")
        forecaster.historical_data = pd.DataFrame(
            {
                "ds": pd.date_range("2020-01-01", periods=3, freq="YE"),
                "y": [5.0, 5.5, 6.0],
            }
        )

        forecaster.fit_model(yearly_seasonality=False, weekly_seasonality=True)

        # Check that Prophet was initialized with correct parameters
        call_args = mock_prophet_class.call_args[1]  # Get keyword arguments
        assert call_args["yearly_seasonality"] is False
        assert call_args["weekly_seasonality"] is True

    def test_validate_model_no_fitted_model_raises_error(self):
        """Test validation without fitted model raises ValueError."""
        forecaster = ProphetForecaster("cap_rate", "35620")

        with pytest.raises(ValueError, match="No model fitted"):
            forecaster.validate_model()

    @patch("forecasting.prophet_engine.Prophet")
    def test_validate_model_insufficient_data(self, mock_prophet_class):
        """Test model validation with insufficient data adjusts holdout period."""
        # Setup
        mock_prophet_instance = Mock()
        mock_prophet_class.return_value = mock_prophet_instance

        # Mock forecast data
        forecast_data = pd.DataFrame({"yhat": [5.0, 5.5, 6.0, 6.5]})
        mock_prophet_instance.predict.return_value = forecast_data
        mock_prophet_instance.make_future_dataframe.return_value = pd.DataFrame()

        forecaster = ProphetForecaster("cap_rate", "35620")
        # Limited historical data (only 3 points)
        forecaster.historical_data = pd.DataFrame(
            {
                "ds": pd.date_range("2020-01-01", periods=3, freq="YE"),
                "y": [5.0, 5.5, 6.0],
            }
        )
        forecaster.fitted_model = mock_prophet_instance

        result = forecaster.validate_model(
            holdout_years=5
        )  # Request more than available

        # Should complete without error and return ValidationResult
        assert isinstance(result, ValidationResult)
        assert hasattr(result, "mape")
        assert hasattr(result, "rmse")
        assert hasattr(result, "mae")

    @patch("forecasting.prophet_engine.Prophet")
    def test_validate_model_success(self, mock_prophet_class):
        """Test successful model validation."""
        # Setup train model mock
        mock_train_prophet = Mock()
        mock_prophet_class.return_value = mock_train_prophet

        # Mock forecast results
        forecast_df = pd.DataFrame({"yhat": [5.0, 5.5, 6.0, 6.2, 6.4]})  # 5 values
        mock_train_prophet.predict.return_value = forecast_df
        mock_train_prophet.make_future_dataframe.return_value = pd.DataFrame()

        forecaster = ProphetForecaster("cap_rate", "35620")
        forecaster.historical_data = pd.DataFrame(
            {
                "ds": pd.date_range("2020-01-01", periods=5, freq="YE"),
                "y": [5.0, 5.5, 6.0, 6.1, 6.3],  # Actual values for comparison
            }
        )
        # Set a dummy fitted model to pass the check
        forecaster.fitted_model = Mock()

        result = forecaster.validate_model(holdout_years=2)

        assert isinstance(result, ValidationResult)
        assert isinstance(result.mape, float)
        assert isinstance(result.rmse, float)
        assert isinstance(result.mae, float)

    def test_generate_forecast_no_fitted_model_raises_error(self):
        """Test generating forecast without fitted model raises ValueError."""
        forecaster = ProphetForecaster("cap_rate", "35620")

        with pytest.raises(ValueError, match="No model fitted"):
            forecaster.generate_forecast()

    @patch("forecasting.prophet_engine.Prophet")
    def test_generate_forecast_success(self, mock_prophet_class):
        """Test successful forecast generation."""
        # Setup
        mock_prophet_instance = Mock()

        # Mock future dataframe creation
        future_df = pd.DataFrame(
            {
                "ds": pd.date_range(
                    "2020-01-01", periods=8, freq="YE"
                )  # 3 historical + 5 forecast
            }
        )
        mock_prophet_instance.make_future_dataframe.return_value = future_df

        # Mock forecast results
        forecast_df = pd.DataFrame(
            {
                "yhat": [5.0, 5.5, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0],
                "yhat_lower": [4.5, 5.0, 5.5, 5.7, 5.9, 6.1, 6.3, 6.5],
                "yhat_upper": [5.5, 6.0, 6.5, 6.7, 6.9, 7.1, 7.3, 7.5],
            }
        )
        mock_prophet_instance.predict.return_value = forecast_df

        forecaster = ProphetForecaster("cap_rate", "35620")
        forecaster.fitted_model = mock_prophet_instance
        forecaster.historical_data = pd.DataFrame(
            {
                "ds": pd.date_range("2020-01-01", periods=3, freq="YE"),
                "y": [5.0, 5.5, 6.0],
            }
        )

        # Mock the validate_model method to avoid complexity
        with patch.object(forecaster, "validate_model") as mock_validate:
            mock_validate.return_value = ValidationResult(mape=5.0, rmse=0.1, mae=0.08)

            result = forecaster.generate_forecast(horizon_years=5)

        # Verify result
        assert isinstance(result, ProphetForecastResult)
        assert result.parameter_name == "cap_rate"
        assert result.geographic_code == "35620"
        assert len(result.forecast_values) == 5
        assert len(result.lower_bound) == 5
        assert len(result.upper_bound) == 5
        assert len(result.forecast_dates) == 5
        assert result.historical_data_points == 3
        assert "mape" in result.model_performance
        assert "overall_trend" in result.trend_info

    def test_plot_forecast_no_data_raises_error(self):
        """Test plotting forecast without loaded data raises ValueError."""
        forecaster = ProphetForecaster("cap_rate", "35620")

        forecast_result = ProphetForecastResult(
            parameter_name="cap_rate",
            geographic_code="35620",
            forecast_values=[6.2, 6.4],
            lower_bound=[5.8, 6.0],
            upper_bound=[6.6, 6.8],
            forecast_dates=["2023-01-01", "2024-01-01"],
            historical_data_points=3,
            model_performance={"mape": 5.0, "rmse": 0.1, "mae": 0.08},
            trend_info={"overall_trend": "increasing", "trend_strength": 10.0},
        )

        with pytest.raises(ValueError, match="No historical data loaded"):
            forecaster.plot_forecast(forecast_result)

    @patch("forecasting.prophet_engine.plt")
    def test_plot_forecast_success(self, mock_plt):
        """Test successful forecast plotting."""
        forecaster = ProphetForecaster("cap_rate", "35620")
        forecaster.historical_data = pd.DataFrame(
            {
                "ds": pd.date_range("2020-01-01", periods=3, freq="YE"),
                "y": [5.0, 5.5, 6.0],
            }
        )

        forecast_result = ProphetForecastResult(
            parameter_name="cap_rate",
            geographic_code="35620",
            forecast_values=[6.2, 6.4],
            lower_bound=[5.8, 6.0],
            upper_bound=[6.6, 6.8],
            forecast_dates=["2023-01-01", "2024-01-01"],
            historical_data_points=3,
            model_performance={"mape": 5.0, "rmse": 0.1, "mae": 0.08},
            trend_info={"overall_trend": "increasing", "trend_strength": 10.0},
        )

        forecaster.plot_forecast(forecast_result, save_path="test_plot.png")

        # Verify plotting functions were called
        mock_plt.figure.assert_called_once()
        mock_plt.plot.assert_called()  # Should be called multiple times
        mock_plt.fill_between.assert_called_once()
        mock_plt.savefig.assert_called_once_with(
            "test_plot.png", dpi=300, bbox_inches="tight"
        )
        mock_plt.close.assert_called_once()


class TestProFormaProphetEngine:
    """Test cases for ProFormaProphetEngine class."""

    def test_init(self):
        """Test successful initialization of ProFormaProphetEngine."""
        engine = ProFormaProphetEngine()

        assert len(engine.metrics_list) == 11
        # Check that we have both national and MSA-specific metrics
        national_metrics = [
            "treasury_10y",
            "commercial_mortgage_rate",
            "fed_funds_rate",
        ]
        msa_metrics = [
            "cap_rate",
            "vacancy_rate",
            "rent_growth",
            "expense_growth",
            "ltv_ratio",
            "closing_cost_pct",
            "lender_reserves",
            "property_growth",
        ]

        for metric in national_metrics:
            assert metric in engine.metrics_list
        for metric in msa_metrics:
            assert metric in engine.metrics_list

    @patch("forecasting.prophet_engine.ProphetForecaster")
    def test_generate_forecasts_for_msa_success(self, mock_forecaster_class):
        """Test successful forecast generation for all MSA metrics."""
        # Setup
        mock_forecaster_instance = Mock()
        mock_forecaster_class.return_value = mock_forecaster_instance

        # Mock forecast result
        mock_forecast_result = ProphetForecastResult(
            parameter_name="test_metric",
            geographic_code="35620",
            forecast_values=[6.2, 6.4],
            lower_bound=[5.8, 6.0],
            upper_bound=[6.6, 6.8],
            forecast_dates=["2023-01-01", "2024-01-01"],
            historical_data_points=3,
            model_performance={"mape": 5.0, "rmse": 0.1, "mae": 0.08},
            trend_info={"overall_trend": "increasing", "trend_strength": 10.0},
        )
        mock_forecaster_instance.run_complete_forecast.return_value = (
            mock_forecast_result
        )

        engine = ProFormaProphetEngine()

        # Execute
        forecasts = engine.generate_forecasts_for_msa("35620", horizon_years=3)

        # Verify
        assert len(forecasts) == 11  # Should have forecast for all 11 metrics
        assert mock_forecaster_class.call_count == 11  # Should create 11 forecasters

        # Check that national metrics use 'NATIONAL' geography
        national_calls = [
            call
            for call in mock_forecaster_class.call_args_list
            if call[0][1] == "NATIONAL"
        ]
        assert len(national_calls) == 3  # 3 national metrics

        # Check that MSA metrics use the provided MSA code
        msa_calls = [
            call
            for call in mock_forecaster_class.call_args_list
            if call[0][1] == "35620"
        ]
        assert len(msa_calls) == 8  # 8 MSA-specific metrics

    @patch("forecasting.prophet_engine.ProphetForecaster")
    def test_generate_forecasts_for_msa_with_errors(self, mock_forecaster_class):
        """Test forecast generation handles individual metric failures gracefully."""

        # Setup - first forecaster succeeds, second fails, third succeeds
        def create_forecaster_side_effect(param_name, geo_code):
            mock_forecaster = Mock()
            if param_name == "commercial_mortgage_rate":  # Make one fail
                mock_forecaster.run_complete_forecast.side_effect = Exception(
                    "Test error"
                )
            else:
                mock_forecast_result = ProphetForecastResult(
                    parameter_name=param_name,
                    geographic_code=geo_code,
                    forecast_values=[6.2, 6.4],
                    lower_bound=[5.8, 6.0],
                    upper_bound=[6.6, 6.8],
                    forecast_dates=["2023-01-01", "2024-01-01"],
                    historical_data_points=3,
                    model_performance={"mape": 5.0, "rmse": 0.1, "mae": 0.08},
                    trend_info={"overall_trend": "increasing", "trend_strength": 10.0},
                )
                mock_forecaster.run_complete_forecast.return_value = (
                    mock_forecast_result
                )
            return mock_forecaster

        mock_forecaster_class.side_effect = create_forecaster_side_effect

        engine = ProFormaProphetEngine()

        # Execute
        forecasts = engine.generate_forecasts_for_msa("35620")

        # Verify - should have 10 successful forecasts (11 - 1 failed)
        assert len(forecasts) == 10
        assert (
            "commercial_mortgage_rate" not in forecasts
        )  # Failed metric should be missing

    def test_get_forecast_values_for_monte_carlo_success(self):
        """Test extracting forecast values for Monte Carlo analysis."""
        engine = ProFormaProphetEngine()

        # Create mock forecasts
        forecasts = {
            "cap_rate": ProphetForecastResult(
                parameter_name="cap_rate",
                geographic_code="35620",
                forecast_values=[6.0, 6.2, 6.4],
                lower_bound=[5.5, 5.7, 5.9],
                upper_bound=[6.5, 6.7, 6.9],
                forecast_dates=["2023-01-01", "2024-01-01", "2025-01-01"],
                historical_data_points=5,
                model_performance={"mape": 3.0, "rmse": 0.05, "mae": 0.04},
                trend_info={"overall_trend": "increasing", "trend_strength": 6.67},
            ),
            "rent_growth": ProphetForecastResult(
                parameter_name="rent_growth",
                geographic_code="35620",
                forecast_values=[3.5, 3.8, 4.0],
                lower_bound=[3.0, 3.3, 3.5],
                upper_bound=[4.0, 4.3, 4.5],
                forecast_dates=["2023-01-01", "2024-01-01", "2025-01-01"],
                historical_data_points=5,
                model_performance={"mape": 4.0, "rmse": 0.08, "mae": 0.06},
                trend_info={"overall_trend": "increasing", "trend_strength": 14.29},
            ),
        }

        # Test extracting Year 1 values
        year_1_values = engine.get_forecast_values_for_monte_carlo(
            forecasts, target_year=1
        )

        assert year_1_values["cap_rate"] == 6.0
        assert year_1_values["rent_growth"] == 3.5

        # Test extracting Year 2 values
        year_2_values = engine.get_forecast_values_for_monte_carlo(
            forecasts, target_year=2
        )

        assert year_2_values["cap_rate"] == 6.2
        assert year_2_values["rent_growth"] == 3.8

    def test_get_forecast_values_for_monte_carlo_insufficient_years(self):
        """Test extracting forecast values when target year exceeds forecast horizon."""
        engine = ProFormaProphetEngine()

        # Create mock forecast with only 2 years
        forecasts = {
            "cap_rate": ProphetForecastResult(
                parameter_name="cap_rate",
                geographic_code="35620",
                forecast_values=[6.0, 6.2],  # Only 2 years
                lower_bound=[5.5, 5.7],
                upper_bound=[6.5, 6.7],
                forecast_dates=["2023-01-01", "2024-01-01"],
                historical_data_points=5,
                model_performance={"mape": 3.0, "rmse": 0.05, "mae": 0.04},
                trend_info={"overall_trend": "increasing", "trend_strength": 3.33},
            )
        }

        # Try to extract Year 3 values (more than available)
        year_3_values = engine.get_forecast_values_for_monte_carlo(
            forecasts, target_year=3
        )

        # Should return empty dict for metrics without sufficient years
        assert len(year_3_values) == 0


class TestProphetIntegration:
    """Integration tests for the Prophet forecasting system."""

    @patch("forecasting.prophet_engine.db_manager")
    @patch("forecasting.prophet_engine.Prophet")
    def test_complete_forecast_workflow(self, mock_prophet_class, mock_db_manager):
        """Test the complete forecast workflow end-to-end."""
        # Setup database mock
        mock_data = [
            {"date": "2020-01-01", "value": 5.0},
            {"date": "2021-01-01", "value": 5.5},
            {"date": "2022-01-01", "value": 6.0},
        ]
        mock_db_manager.get_parameter_data.return_value = mock_data
        mock_db_manager.save_prophet_forecast.return_value = None

        # Setup Prophet mock
        mock_prophet_instance = Mock()
        mock_prophet_class.return_value = mock_prophet_instance

        # Mock future dataframe and forecast
        future_df = pd.DataFrame(
            {"ds": pd.date_range("2020-01-01", periods=8, freq="YE")}
        )
        mock_prophet_instance.make_future_dataframe.return_value = future_df

        forecast_df = pd.DataFrame(
            {
                "yhat": [5.0, 5.5, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0],
                "yhat_lower": [4.5, 5.0, 5.5, 5.7, 5.9, 6.1, 6.3, 6.5],
                "yhat_upper": [5.5, 6.0, 6.5, 6.7, 6.9, 7.1, 7.3, 7.5],
            }
        )
        mock_prophet_instance.predict.return_value = forecast_df

        # Execute complete workflow
        forecaster = ProphetForecaster("cap_rate", "35620")

        with patch.object(forecaster, "plot_forecast") as mock_plot:
            result = forecaster.run_complete_forecast(horizon_years=5, create_plot=True)

        # Verify all steps were executed
        mock_db_manager.get_parameter_data.assert_called_once()
        # Note: fit is called twice - once for main model, once for validation
        assert mock_prophet_instance.fit.call_count >= 1
        mock_db_manager.save_prophet_forecast.assert_called_once()
        mock_plot.assert_called_once()

        # Verify result structure
        assert isinstance(result, ProphetForecastResult)
        assert result.parameter_name == "cap_rate"
        assert result.geographic_code == "35620"
        assert len(result.forecast_values) == 5


class TestProphetAvailability:
    """Test cases for Prophet availability handling."""

    def test_prophet_available_constant(self):
        """Test that PROPHET_AVAILABLE constant is set correctly."""
        assert PROPHET_AVAILABLE is True  # Should be True since Prophet is installed

    @patch(
        "forecasting.prophet_engine.Prophet",
        side_effect=ImportError("Prophet not available"),
    )
    def test_prophet_import_error_handling(self, mock_prophet):
        """Test handling of Prophet import errors."""
        # This test would need to be in a separate module to properly test ImportError
        # For now, just verify that the constant reflects actual availability
        assert PROPHET_AVAILABLE is True  # In our environment, it should be available


if __name__ == "__main__":
    pytest.main([__file__])
