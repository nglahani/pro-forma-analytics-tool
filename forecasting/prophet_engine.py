#!/usr/bin/env python3
"""
Prophet Forecasting Engine

Implements Meta's Prophet time series forecasting for the 11 pro forma metrics.
Generates forecasts with uncertainty intervals and automatic trend/seasonality detection.
"""

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from prophet import Prophet

    PROPHET_AVAILABLE = True
except ImportError as e:
    raise ImportError(
        "Prophet is required for forecasting. Install with: pip install prophet==1.1.7"
    ) from e

from core.exceptions import ValidationError
from core.logging_config import get_logger

# Import from project modules
from data.databases.database_manager import db_manager

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


@dataclass
class ProphetForecastResult:
    """Result object for Prophet forecasts."""

    parameter_name: str
    geographic_code: str
    forecast_values: List[float]
    lower_bound: List[float]
    upper_bound: List[float]
    forecast_dates: List[str]
    historical_data_points: int
    model_performance: Dict[str, float]
    trend_info: Dict[str, Any]


@dataclass
class ValidationResult:
    """Result object for model validation."""

    mape: float  # Mean Absolute Percentage Error
    rmse: float  # Root Mean Square Error
    mae: float  # Mean Absolute Error


class ProphetForecaster:
    """Prophet forecasting engine for pro forma metrics."""

    def __init__(self, parameter_name: str, geographic_code: str):
        """
        Initialize forecaster for specific parameter and geography.

        Args:
            parameter_name: Name of the pro forma metric
            geographic_code: Geographic identifier (MSA code or 'NATIONAL')
        """
        self.parameter_name = parameter_name
        self.geographic_code = geographic_code
        self.historical_data = None
        self.fitted_model = None
        self.logger = get_logger(__name__)

        # Validate inputs
        if not parameter_name or not geographic_code:
            raise ValidationError("Parameter name and geographic code are required")

        self.logger.info(
            f"Initialized ProphetForecaster for {parameter_name} ({geographic_code})"
        )

    def load_historical_data(self) -> pd.DataFrame:
        """Load historical data for the parameter and geography."""

        try:
            # Use the database manager's parameter mapping
            data_points = db_manager.get_parameter_data(
                self.parameter_name, self.geographic_code
            )

            if not data_points:
                raise ValueError(
                    f"No historical data found for {self.parameter_name} in {self.geographic_code}"
                )

            # Convert to pandas DataFrame in Prophet format (ds, y)
            df = pd.DataFrame(data_points)
            df["ds"] = pd.to_datetime(df["date"])  # Prophet requires 'ds' column
            df["y"] = df["value"]  # Prophet requires 'y' column
            df = df.sort_values("ds")

            # Handle duplicate dates by taking the last value
            df = df.drop_duplicates(subset=["ds"], keep="last")

            self.historical_data = df[["ds", "y"]]

            print(
                f"Loaded {len(self.historical_data)} data points for {self.parameter_name} ({self.geographic_code})"
            )
            print(
                f"Date range: {self.historical_data['ds'].min().strftime('%Y-%m-%d')} to {self.historical_data['ds'].max().strftime('%Y-%m-%d')}"
            )

            return self.historical_data

        except Exception as e:
            raise Exception(f"Failed to load historical data: {str(e)}")

    def fit_model(
        self,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = False,
        daily_seasonality: bool = False,
    ) -> None:
        """
        Fit Prophet model to historical data.

        Args:
            yearly_seasonality: Include yearly seasonality
            weekly_seasonality: Include weekly seasonality
            daily_seasonality: Include daily seasonality
        """
        if self.historical_data is None:
            raise ValueError(
                "No historical data loaded. Call load_historical_data() first."
            )

        try:
            # Configure Prophet model
            self.fitted_model = Prophet(
                yearly_seasonality=yearly_seasonality,
                weekly_seasonality=weekly_seasonality,
                daily_seasonality=daily_seasonality,
                interval_width=0.95,  # 95% confidence intervals
                changepoint_prior_scale=0.05,  # Flexibility of trend changes
                seasonality_prior_scale=10.0,  # Flexibility of seasonality
                uncertainty_samples=1000,  # Samples for uncertainty estimation
            )

            # Fit the model
            self.fitted_model.fit(self.historical_data)

            print(f"Fitted Prophet model successfully")

        except Exception as e:
            raise Exception(f"Failed to fit Prophet model: {str(e)}")

    def validate_model(self, holdout_years: int = 3) -> ValidationResult:
        """
        Validate the fitted model using holdout data.

        Args:
            holdout_years: Number of years to hold out for validation

        Returns:
            ValidationResult with validation metrics
        """
        if self.fitted_model is None:
            raise ValueError("No model fitted. Call fit_model() first.")

        if len(self.historical_data) < holdout_years + 3:
            print(
                f"Warning: Not enough data for {holdout_years}-year holdout validation"
            )
            holdout_years = max(1, len(self.historical_data) // 3)

        # Split data
        train_data = self.historical_data[:-holdout_years].copy()
        test_data = self.historical_data[-holdout_years:].copy()

        # Fit model on training data
        train_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            interval_width=0.95,
        )
        train_model.fit(train_data)

        # Generate forecasts for test period
        future = train_model.make_future_dataframe(periods=holdout_years, freq="Y")
        forecast = train_model.predict(future)

        # Get forecast values for test period
        forecast_values = forecast["yhat"].tail(holdout_years).values
        actual_values = test_data["y"].values

        # Calculate validation metrics
        errors = actual_values - forecast_values
        mape = np.mean(np.abs(errors / actual_values)) * 100
        rmse = np.sqrt(np.mean(errors**2))
        mae = np.mean(np.abs(errors))

        return ValidationResult(mape=mape, rmse=rmse, mae=mae)

    def generate_forecast(self, horizon_years: int = 5) -> ProphetForecastResult:
        """
        Generate forecast with uncertainty intervals.

        Args:
            horizon_years: Number of years to forecast

        Returns:
            ProphetForecastResult with forecasts and metadata
        """
        if self.fitted_model is None:
            raise ValueError("No model fitted. Call fit_model() first.")

        try:
            # Create future dataframe
            future = self.fitted_model.make_future_dataframe(
                periods=horizon_years, freq="Y"
            )

            # Generate forecast
            forecast = self.fitted_model.predict(future)

            # Extract forecast values (only the future periods)
            forecast_data = forecast.tail(horizon_years)
            forecast_values = forecast_data["yhat"].tolist()
            lower_bound = forecast_data["yhat_lower"].tolist()
            upper_bound = forecast_data["yhat_upper"].tolist()

            # Generate forecast dates
            forecast_dates = []
            last_date = self.historical_data["ds"].max()
            for i in range(1, horizon_years + 1):
                next_year = last_date.year + i
                forecast_dates.append(f"{next_year}-01-01")

            # Model performance metrics
            validation = self.validate_model()
            model_performance = {
                "mape": validation.mape,
                "rmse": validation.rmse,
                "mae": validation.mae,
            }

            # Trend information
            trend_info = {
                "overall_trend": (
                    "increasing"
                    if forecast_values[-1] > forecast_values[0]
                    else "decreasing"
                ),
                "trend_strength": abs(forecast_values[-1] - forecast_values[0])
                / forecast_values[0]
                * 100,
            }

            return ProphetForecastResult(
                parameter_name=self.parameter_name,
                geographic_code=self.geographic_code,
                forecast_values=forecast_values,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                forecast_dates=forecast_dates,
                historical_data_points=len(self.historical_data),
                model_performance=model_performance,
                trend_info=trend_info,
            )

        except Exception as e:
            raise Exception(f"Failed to generate forecast: {str(e)}")

    def plot_forecast(
        self, forecast_result: ProphetForecastResult, save_path: Optional[str] = None
    ) -> None:
        """
        Create a line graph showing historical data in blue and forecasted data in red.

        Args:
            forecast_result: ProphetForecastResult object with forecast data
            save_path: Optional path to save the plot
        """
        if self.historical_data is None:
            raise ValueError("No historical data loaded.")

        plt.figure(figsize=(12, 8))

        # Plot historical data in blue
        historical_dates = self.historical_data["ds"]
        historical_values = self.historical_data["y"]
        plt.plot(
            historical_dates,
            historical_values,
            "b-",
            linewidth=2,
            label="Historical Data",
            alpha=0.8,
        )

        # Create forecast dates
        forecast_dates = [pd.Timestamp(date) for date in forecast_result.forecast_dates]

        # Connect historical data to forecast by including the last historical point
        last_historical_date = historical_dates.iloc[-1]
        last_historical_value = historical_values.iloc[-1]

        # Create connected forecast line (include last historical point)
        connected_dates = [last_historical_date] + forecast_dates
        connected_values = [last_historical_value] + forecast_result.forecast_values
        connected_lower = [last_historical_value] + forecast_result.lower_bound
        connected_upper = [last_historical_value] + forecast_result.upper_bound

        # Plot forecasted data in red (connected to historical)
        plt.plot(
            connected_dates,
            connected_values,
            "r-",
            linewidth=2,
            label="Forecast",
            alpha=0.8,
        )

        # Add uncertainty intervals (connected to historical)
        plt.fill_between(
            connected_dates,
            connected_lower,
            connected_upper,
            color="red",
            alpha=0.2,
            label="95% Confidence Interval",
        )

        # Formatting
        plt.title(
            f"Prophet Forecast: {forecast_result.parameter_name} ({forecast_result.geographic_code})",
            fontsize=16,
            fontweight="bold",
        )
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Value", fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)

        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(2))  # Every 2 years
        plt.xticks(rotation=45)

        # Add model info
        info_text = f"MAPE: {forecast_result.model_performance['mape']:.2f}%\\nTrend: {forecast_result.trend_info['overall_trend']}\\nData Points: {forecast_result.historical_data_points}"
        plt.text(
            0.02,
            0.98,
            info_text,
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Plot saved to: {save_path}")
        else:
            plt.show()

        plt.close()

    def run_complete_forecast(
        self,
        horizon_years: int = 5,
        create_plot: bool = True,
        save_plot_path: Optional[str] = None,
    ) -> ProphetForecastResult:
        """
        Complete forecasting workflow: load data, fit model, generate forecast.

        Args:
            horizon_years: Number of years to forecast
            create_plot: Whether to create visualization
            save_plot_path: Optional path to save the plot

        Returns:
            ProphetForecastResult with complete forecast
        """
        print(f"\n{'='*60}")
        print(f"PROPHET FORECASTING: {self.parameter_name} ({self.geographic_code})")
        print(f"{'='*60}")

        # Step 1: Load historical data
        self.load_historical_data()

        # Step 2: Fit model
        self.fit_model()

        # Step 3: Generate forecast
        forecast_result = self.generate_forecast(horizon_years)

        # Step 4: Display results
        print(f"\nForecast Results ({horizon_years} years):")
        for i, (date, value) in enumerate(
            zip(forecast_result.forecast_dates, forecast_result.forecast_values)
        ):
            print(f"  {date}: {value:.4f}")

        print(f"\nModel Performance:")
        print(f"  MAPE: {forecast_result.model_performance['mape']:.2f}%")
        print(f"  RMSE: {forecast_result.model_performance['rmse']:.4f}")
        print(f"  Trend: {forecast_result.trend_info['overall_trend']}")

        # Step 5: Save forecast to database
        try:
            db_manager.save_prophet_forecast(
                parameter_name=self.parameter_name,
                geographic_code=self.geographic_code,
                forecast_horizon_years=horizon_years,
                forecast_values=forecast_result.forecast_values,
                forecast_dates=forecast_result.forecast_dates,
                lower_bound=forecast_result.lower_bound,
                upper_bound=forecast_result.upper_bound,
                model_performance=forecast_result.model_performance,
                trend_info=forecast_result.trend_info,
                historical_data_points=forecast_result.historical_data_points,
            )
            print(f"Forecast saved to database")
        except Exception as e:
            print(f"Warning: Failed to save forecast to database: {e}")

        # Step 6: Create visualization if requested
        if create_plot:
            if save_plot_path is None:
                # Create default save path
                plots_dir = Path("forecast_plots")
                plots_dir.mkdir(exist_ok=True)
                save_plot_path = (
                    plots_dir
                    / f"{self.parameter_name}_{self.geographic_code}_prophet_forecast.png"
                )

            self.plot_forecast(forecast_result, str(save_plot_path))

        return forecast_result


class ProFormaProphetEngine:
    """Main engine for generating Prophet forecasts for all 11 pro forma metrics."""

    def __init__(self):
        """Initialize the pro forma Prophet engine."""

        # Define the 11 pro forma metrics
        self.metrics_list = [
            # National (3 metrics)
            "treasury_10y",
            "commercial_mortgage_rate",
            "fed_funds_rate",
            # MSA-specific (8 metrics)
            "cap_rate",
            "vacancy_rate",
            "rent_growth",
            "expense_growth",
            "ltv_ratio",
            "closing_cost_pct",
            "lender_reserves",
            "property_growth",
        ]

    def generate_forecasts_for_msa(
        self, msa_code: str, horizon_years: int = 5
    ) -> Dict[str, ProphetForecastResult]:
        """
        Generate Prophet forecasts for all 11 metrics for a specific MSA.

        Args:
            msa_code: MSA code (e.g., '35620' for NYC)
            horizon_years: Forecast horizon

        Returns:
            Dictionary mapping metric names to ProphetForecastResult objects
        """
        forecasts = {}
        errors = []

        print(f"\n{'#'*80}")
        print(f"GENERATING PROPHET FORECASTS FOR MSA: {msa_code}")
        print(f"FORECAST HORIZON: {horizon_years} YEARS")
        print(f"{'#'*80}")

        for metric_name in self.metrics_list:
            try:
                # Determine geography for this metric
                if metric_name in [
                    "treasury_10y",
                    "commercial_mortgage_rate",
                    "fed_funds_rate",
                ]:
                    geography = "NATIONAL"
                else:
                    geography = msa_code

                # Create forecaster and run forecast
                forecaster = ProphetForecaster(metric_name, geography)
                forecast_result = forecaster.run_complete_forecast(horizon_years)

                forecasts[metric_name] = forecast_result

            except Exception as e:
                error_msg = f"Failed to forecast {metric_name}: {str(e)}"
                errors.append(error_msg)
                print(f"ERROR: {error_msg}")

        # Summary
        print(f"\n{'='*80}")
        print(f"FORECAST SUMMARY FOR MSA {msa_code}")
        print(f"{'='*80}")
        print(f"Successful forecasts: {len(forecasts)}/11 metrics")
        if errors:
            print(f"Errors: {len(errors)}")
            for error in errors:
                print(f"  - {error}")

        return forecasts

    def get_forecast_values_for_monte_carlo(
        self, forecasts: Dict[str, ProphetForecastResult], target_year: int = 1
    ) -> Dict[str, float]:
        """
        Extract specific year forecast values for Monte Carlo analysis.

        Args:
            forecasts: Dictionary of ProphetForecastResult objects
            target_year: Which forecast year to extract (1-based, so 1 = first year)

        Returns:
            Dictionary mapping metric names to forecast values for the target year
        """
        monte_carlo_inputs = {}

        for metric_name, forecast_result in forecasts.items():
            if target_year <= len(forecast_result.forecast_values):
                value = forecast_result.forecast_values[
                    target_year - 1
                ]  # Convert to 0-based index
                monte_carlo_inputs[metric_name] = value
            else:
                print(
                    f"Warning: {metric_name} forecast doesn't have {target_year} years of data"
                )

        return monte_carlo_inputs


def main():
    """Test the Prophet forecasting system."""

    # Initialize engine
    engine = ProFormaProphetEngine()

    # Test with NYC MSA
    msa_code = "35620"  # NYC
    forecasts = engine.generate_forecasts_for_msa(msa_code, horizon_years=5)

    # Extract Year 1 values for Monte Carlo
    year_1_values = engine.get_forecast_values_for_monte_carlo(forecasts, target_year=1)

    print(f"\n{'='*60}")
    print("YEAR 1 FORECAST VALUES FOR MONTE CARLO")
    print(f"{'='*60}")
    for metric, value in year_1_values.items():
        print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()
