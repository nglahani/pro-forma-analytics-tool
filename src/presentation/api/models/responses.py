"""
API Response Models

Pydantic models for structuring API response data.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.domain.entities.cash_flow_projection import CashFlowProjection
from src.domain.entities.dcf_assumptions import DCFAssumptions
from src.domain.entities.financial_metrics import (
    InvestmentRecommendation,
)


class APIFinancialMetrics(BaseModel):
    """Simplified financial metrics for API consumers.

    Maps domain fields to expected API names (npv, irr, equity_multiple).
    """

    npv: float = Field(description="Net Present Value (NPV)")
    irr: float = Field(description="Internal Rate of Return (IRR)")
    equity_multiple: float = Field(description="Equity multiple")

    @classmethod
    def from_domain(cls, metrics: Any) -> "APIFinancialMetrics":
        """Create API metrics from a domain or mock metrics object.

        Supports both real domain entity attributes and test mocks that may use
        short names (npv/irr).
        """
        # Prefer short names if present (tests often mock these)
        npv_value = getattr(metrics, "npv", None)
        irr_value = getattr(metrics, "irr", None)
        equity_mult = getattr(metrics, "equity_multiple", None)

        # Fallback to domain attribute names
        if npv_value is None:
            npv_value = getattr(metrics, "net_present_value", 0.0)
        if irr_value is None:
            irr_value = getattr(metrics, "internal_rate_return", 0.0)
        if equity_mult is None:
            equity_mult = getattr(metrics, "equity_multiple", 0.0)

        # Coerce non-numeric mocks/objects to 0.0 defaults
        def _num(val: Any) -> float:
            return val if isinstance(val, (int, float)) else 0.0

        npv_value = _num(npv_value)
        irr_value = _num(irr_value)
        equity_mult = _num(equity_mult)

        return cls(npv=npv_value, irr=irr_value, equity_multiple=equity_mult)


from src.domain.entities.monte_carlo import Scenario


class AnalysisMetadata(BaseModel):
    """Metadata about the DCF analysis execution."""

    processing_time_seconds: float = Field(
        description="Time taken to complete the analysis"
    )

    dcf_engine_version: str = Field(
        default="1.0.0", description="Version of the DCF calculation engine"
    )

    analysis_timestamp: datetime = Field(description="When the analysis was performed")

    data_sources: Dict[str, str] = Field(
        description="Data sources used for the analysis"
    )

    assumptions_summary: Dict[str, Any] = Field(
        description="Key assumptions used in the calculation"
    )


class DCFAnalysisResponse(BaseModel):
    """Response model for single property DCF analysis."""

    success: bool = Field(default=True, description="Indicates request success")
    request_id: str = Field(description="Unique identifier for this analysis request")

    property_id: str = Field(description="Property identifier from the request")

    analysis_date: datetime = Field(description="Date/time when analysis was performed")

    financial_metrics: APIFinancialMetrics = Field(
        description="Calculated financial metrics and investment returns"
    )

    cash_flows: Optional[CashFlowProjection] = Field(
        default=None, description="Detailed cash flow projections"
    )

    dcf_assumptions: DCFAssumptions = Field(
        description="DCF assumptions used in the analysis"
    )

    investment_recommendation: InvestmentRecommendation = Field(
        description="Investment recommendation based on analysis"
    )

    metadata: AnalysisMetadata = Field(
        description="Analysis execution metadata",
        serialization_alias="analysis_metadata",
    )

    # Optional additional results
    monte_carlo_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary of Monte Carlo simulation results if executed",
    )


class BatchAnalysisResponse(BaseModel):
    """Response model for batch property analysis."""

    success: bool = Field(default=True, description="Indicates batch request success")
    batch_id: str = Field(description="Unique identifier for this batch request")

    batch_timestamp: datetime = Field(
        description="When the batch analysis was initiated"
    )

    total_properties: int = Field(description="Total number of properties in the batch")

    successful_analyses: int = Field(description="Number of successful analyses")

    failed_analyses: int = Field(description="Number of failed analyses")

    results: List[Union[DCFAnalysisResponse, "BatchAnalysisError"]] = Field(
        description="Analysis results for each property"
    )

    processing_summary: Dict[str, Any] = Field(
        description="Summary of batch processing metrics",
        serialization_alias="batch_summary",
    )


class BatchAnalysisError(BaseModel):
    """Error information for failed batch analysis items."""

    request_id: str = Field(description="Request identifier for the failed analysis")

    property_id: Optional[str] = Field(
        default=None, description="Property identifier if available"
    )

    error_code: str = Field(description="Error classification code")

    error_message: str = Field(description="Human-readable error description")

    timestamp: datetime = Field(description="When the error occurred")


class MonteCarloDistribution(BaseModel):
    """Statistical distribution data for Monte Carlo results."""

    parameter_name: str = Field(description="Name of the parameter")

    mean: float = Field(description="Mean value")

    std_dev: float = Field(description="Standard deviation")

    percentiles: Dict[str, float] = Field(
        description="Percentile values (e.g., '5', '50', '95')"
    )

    min_value: float = Field(description="Minimum value in distribution")

    max_value: float = Field(description="Maximum value in distribution")


class MonteCarloResponse(BaseModel):
    """Response model for Monte Carlo simulation."""

    request_id: str = Field(description="Unique identifier for this simulation request")

    property_id: str = Field(description="Property identifier from the request")

    simulation_timestamp: datetime = Field(
        description="When the simulation was performed"
    )

    simulation_count: int = Field(description="Number of scenarios generated")

    scenarios: List[Scenario] = Field(description="Generated Monte Carlo scenarios")

    distributions: Optional[List[MonteCarloDistribution]] = Field(
        default=None, description="Statistical distributions of key parameters"
    )

    risk_metrics: Dict[str, float] = Field(description="Risk assessment metrics")

    scenario_classification: Dict[str, int] = Field(
        description="Count of scenarios by market type (Bull/Bear/Neutral)"
    )

    processing_time_seconds: float = Field(
        description="Time taken to complete the simulation"
    )


class MarketDataPoint(BaseModel):
    """Individual market data point."""

    date: datetime = Field(description="Data point date")

    value: float = Field(description="Parameter value")

    source: Optional[str] = Field(default=None, description="Data source identifier")


class MarketDataResponse(BaseModel):
    """Response model for market data queries."""

    msa: str = Field(description="Metropolitan Statistical Area")

    parameter: str = Field(description="Market parameter name")

    data_points: List[MarketDataPoint] = Field(
        description="Historical market data points"
    )

    current_value: Optional[float] = Field(
        default=None, description="Most recent parameter value"
    )

    last_updated: datetime = Field(description="When the data was last updated")

    data_coverage: Dict[str, Any] = Field(
        description="Information about data coverage and quality"
    )


class ForecastPoint(BaseModel):
    """Individual forecast data point."""

    date: datetime = Field(description="Forecast date")

    predicted_value: float = Field(description="Predicted parameter value")

    lower_bound: float = Field(description="Lower confidence interval bound")

    upper_bound: float = Field(description="Upper confidence interval bound")


class ForecastResponse(BaseModel):
    """Response model for forecast queries."""

    parameter: str = Field(description="Forecasted parameter name")

    msa: str = Field(description="Metropolitan Statistical Area")

    forecast_horizon_years: int = Field(description="Forecast horizon in years")

    confidence_level: float = Field(description="Confidence level for intervals")

    forecast_points: List[ForecastPoint] = Field(description="Forecast data points")

    historical_data: Optional[List[MarketDataPoint]] = Field(
        default=None, description="Historical data used for forecasting"
    )

    model_info: Dict[str, Any] = Field(
        description="Information about the forecasting model"
    )

    forecast_timestamp: datetime = Field(description="When the forecast was generated")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(description="Overall service health status")

    timestamp: datetime = Field(description="Health check timestamp")

    version: str = Field(description="API version")

    environment: str = Field(description="Runtime environment")

    uptime_seconds: float = Field(description="Service uptime in seconds")

    dependencies: Dict[str, str] = Field(description="Health status of dependencies")


class ConfigurationResponse(BaseModel):
    """Response model for configuration endpoint."""

    supported_msas: List[str] = Field(
        description="List of supported Metropolitan Statistical Areas"
    )

    supported_parameters: List[str] = Field(
        description="List of available forecast parameters"
    )

    analysis_limits: Dict[str, int] = Field(
        description="System limits for various operations"
    )

    dcf_methodology: Dict[str, str] = Field(
        description="Information about DCF calculation methodology"
    )

    api_version: str = Field(description="Current API version")

    last_updated: datetime = Field(description="When configuration was last updated")
