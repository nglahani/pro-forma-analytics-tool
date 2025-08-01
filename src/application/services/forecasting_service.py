"""
Forecasting Application Service

Orchestrates forecasting workflows without containing business logic.
Follows clean architecture principles with proper dependency injection.
"""

import logging
from datetime import date
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from forecasting.prophet_engine import ProFormaProphetEngine

from ...domain.entities.forecast import (
    ForecastRequest,
    ForecastResult,
    ParameterId,
)
from ...domain.repositories.parameter_repository import (
    ForecastRepository,
    ParameterRepository,
)


class ForecastingApplicationService:
    """Application service for forecasting workflows."""

    def __init__(
        self,
        parameter_repository: ParameterRepository,
        forecast_repository: ForecastRepository,
        forecasting_engine: "ProFormaProphetEngine",  # Forward reference
        logger: Optional[logging.Logger] = None,
    ):
        self._parameter_repo = parameter_repository
        self._forecast_repo = forecast_repository
        self._forecasting_engine = forecasting_engine
        self._logger = logger or logging.getLogger(__name__)

    def generate_forecast(self, request: ForecastRequest) -> ForecastResult:
        """
        Generate a forecast for a parameter.

        This method orchestrates the forecasting workflow:
        1. Check for cached forecast
        2. Load historical data if needed
        3. Generate new forecast
        4. Cache the result

        Args:
            request: Forecast request with parameters

        Returns:
            ForecastResult containing the forecast

        Raises:
            ValueError: If request is invalid
            DataNotFoundError: If historical data is insufficient
            ForecastError: If forecast generation fails
        """
        self._logger.info(
            f"Generating forecast for {request.parameter_id.name} "
            f"({request.parameter_id.geographic_code}), "
            f"{request.horizon_years} years horizon"
        )

        # Step 1: Check for cached forecast
        cached_forecast = self._forecast_repo.get_cached_forecast(
            request.parameter_id,
            request.horizon_years,
            request.model_type,
            max_age_days=30,
        )

        if cached_forecast:
            self._logger.info("Using cached forecast")
            return cached_forecast

        # Step 2: Load historical data
        historical_data = self._parameter_repo.get_historical_data(request.parameter_id)

        if not historical_data:
            raise DataNotFoundError(
                f"No historical data found for parameter {request.parameter_id.name}"
            )

        if len(historical_data.data_points) < 24:  # Minimum 2 years of monthly data
            raise DataNotFoundError(
                f"Insufficient historical data for {request.parameter_id.name}: "
                f"got {len(historical_data.data_points)} points, need at least 24"
            )

        # Step 3: Generate forecast using domain service
        try:
            forecast_result = self._forecasting_engine.generate_forecast(
                request, historical_data
            )
        except Exception as e:
            self._logger.error(f"Forecast generation failed: {e}")
            raise ForecastError(f"Failed to generate forecast: {e}") from e

        # Step 4: Cache the result
        try:
            self._forecast_repo.save_forecast(forecast_result)
            self._logger.info(f"Cached forecast {forecast_result.forecast_id}")
        except Exception as e:
            self._logger.warning(f"Failed to cache forecast: {e}")
            # Don't fail the request if caching fails

        return forecast_result

    def generate_multiple_forecasts(
        self,
        parameter_ids: List[ParameterId],
        horizon_years: int,
        model_type: str = "prophet",
        confidence_level: float = 0.95,
    ) -> Dict[ParameterId, ForecastResult]:
        """
        Generate forecasts for multiple parameters efficiently.

        Args:
            parameter_ids: List of parameters to forecast
            horizon_years: Forecast horizon in years
            model_type: Type of forecasting model
            confidence_level: Confidence level for intervals

        Returns:
            Dictionary mapping parameter IDs to forecast results
        """
        self._logger.info(
            f"Generating {len(parameter_ids)} forecasts for "
            f"{horizon_years} years using {model_type}"
        )

        results = {}
        errors = []

        # First, try to get cached forecasts
        cached_forecasts = self._forecast_repo.get_forecasts_for_simulation(
            parameter_ids, horizon_years, model_type, max_age_days=30
        )

        for parameter_id in parameter_ids:
            if parameter_id in cached_forecasts:
                results[parameter_id] = cached_forecasts[parameter_id]
                continue

            try:
                request = ForecastRequest(
                    parameter_id=parameter_id,
                    horizon_years=horizon_years,
                    model_type=model_type,
                    confidence_level=confidence_level,
                )
                forecast = self.generate_forecast(request)
                results[parameter_id] = forecast

            except Exception as e:
                error_msg = f"Failed to forecast {parameter_id.name}: {e}"
                self._logger.error(error_msg)
                errors.append(error_msg)

        if errors and not results:
            raise ForecastError(f"All forecasts failed: {'; '.join(errors)}")

        if errors:
            self._logger.warning(f"Some forecasts failed: {'; '.join(errors)}")

        self._logger.info(f"Successfully generated {len(results)} forecasts")
        return results

    def validate_forecast_quality(
        self,
        forecast_result: ForecastResult,
        quality_thresholds: Optional[Dict[str, float]] = None,
    ) -> bool:
        """
        Validate forecast quality against thresholds.

        Args:
            forecast_result: Forecast to validate
            quality_thresholds: Optional quality thresholds

        Returns:
            True if forecast meets quality standards
        """
        default_thresholds = {"mae": 0.1, "mape": 15.0, "rmse": 0.15, "r_squared": 0.7}

        thresholds = quality_thresholds or default_thresholds

        is_acceptable = forecast_result.model_performance.is_acceptable(thresholds)

        if not is_acceptable:
            self._logger.warning(
                f"Forecast {forecast_result.forecast_id} failed quality check: "
                f"MAE={forecast_result.model_performance.mae:.3f}, "
                f"MAPE={forecast_result.model_performance.mape:.1f}%, "
                f"RMSE={forecast_result.model_performance.rmse:.3f}, "
                f"R²={forecast_result.model_performance.r_squared:.3f}"
            )

        return is_acceptable

    def get_data_completeness_report(
        self, parameter_ids: List[ParameterId], start_date: date, end_date: date
    ) -> Dict[ParameterId, float]:
        """
        Generate a data completeness report for multiple parameters.

        Args:
            parameter_ids: Parameters to check
            start_date: Start date for completeness check
            end_date: End date for completeness check

        Returns:
            Dictionary mapping parameter IDs to completeness percentages
        """
        completeness_report = {}

        for parameter_id in parameter_ids:
            try:
                completeness = self._parameter_repo.get_data_completeness(
                    parameter_id, start_date, end_date
                )
                completeness_report[parameter_id] = completeness
            except Exception as e:
                self._logger.error(
                    f"Failed to check completeness for {parameter_id.name}: {e}"
                )
                completeness_report[parameter_id] = 0.0

        return completeness_report


# Custom exceptions for the application layer
class ForecastError(Exception):
    """Raised when forecast generation fails."""


class DataNotFoundError(Exception):
    """Raised when required data is not found."""
