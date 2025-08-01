"""
API Request Models

Pydantic models for validating and serializing API request data.
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.domain.entities.property_data import SimplifiedPropertyInput


class AnalysisOptions(BaseModel):
    """Configuration options for DCF analysis."""

    monte_carlo_simulations: int = Field(
        default=10000,
        ge=500,
        le=50000,
        description="Number of Monte Carlo simulations to run",
    )

    forecast_horizon_years: int = Field(
        default=6, ge=3, le=10, description="Forecast horizon in years"
    )

    include_scenarios: bool = Field(
        default=True, description="Include scenario analysis in results"
    )

    confidence_level: float = Field(
        default=0.95,
        ge=0.8,
        le=0.99,
        description="Confidence level for forecasts and risk metrics",
    )

    detailed_cash_flows: bool = Field(
        default=True, description="Include detailed cash flow projections in response"
    )


class PropertyAnalysisRequest(BaseModel):
    """Request model for single property DCF analysis."""

    property_data: SimplifiedPropertyInput = Field(
        description="Property information and investment parameters"
    )

    options: Optional[AnalysisOptions] = Field(
        default=None, description="Analysis configuration options"
    )

    request_id: Optional[str] = Field(
        default=None, description="Client-provided request identifier"
    )

    @validator("options", pre=True, always=True)
    def set_default_options(cls, v):
        """Set default options if not provided."""
        return v or AnalysisOptions()


class BatchAnalysisRequest(BaseModel):
    """Request model for batch property analysis."""

    properties: List[PropertyAnalysisRequest] = Field(
        description="List of properties to analyze", min_items=1, max_items=50
    )

    parallel_processing: bool = Field(
        default=True, description="Enable parallel processing of properties"
    )

    max_concurrent: int = Field(
        default=10, ge=1, le=50, description="Maximum concurrent property analyses"
    )

    batch_id: Optional[str] = Field(
        default=None, description="Client-provided batch identifier"
    )

    @validator("properties")
    def validate_properties(cls, v):
        """Validate properties list."""
        if len(v) > 50:
            raise ValueError("Maximum 50 properties allowed per batch")
        return v


class MonteCarloRequest(BaseModel):
    """Request model for Monte Carlo simulation."""

    property_data: SimplifiedPropertyInput = Field(
        description="Property information for simulation"
    )

    simulation_count: int = Field(
        default=10000,
        ge=500,
        le=50000,
        description="Number of Monte Carlo scenarios to generate",
    )

    correlation_window_years: int = Field(
        default=5,
        ge=3,
        le=15,
        description="Historical data window for correlation analysis",
    )

    include_distributions: bool = Field(
        default=True, description="Include probability distributions in response"
    )

    percentiles: List[float] = Field(
        default=[5, 10, 25, 50, 75, 90, 95],
        description="Percentiles to calculate for risk metrics",
    )

    request_id: Optional[str] = Field(
        default=None, description="Client-provided request identifier"
    )

    @validator("percentiles")
    def validate_percentiles(cls, v):
        """Validate percentiles are within valid range."""
        for p in v:
            if not 0 < p < 100:
                raise ValueError("Percentiles must be between 0 and 100")
        return sorted(v)


class MarketDataRequest(BaseModel):
    """Request model for market data queries."""

    msa: str = Field(description="Metropolitan Statistical Area code")

    parameters: Optional[List[str]] = Field(
        default=None, description="Specific parameters to retrieve"
    )

    start_date: Optional[date] = Field(
        default=None, description="Start date for historical data"
    )

    end_date: Optional[date] = Field(
        default=None, description="End date for historical data"
    )

    @validator("msa")
    def validate_msa(cls, v):
        """Validate MSA is supported."""
        supported_msas = ["NYC", "LA", "Chicago", "DC", "Miami"]
        if v not in supported_msas:
            raise ValueError(f"MSA must be one of: {supported_msas}")
        return v


class ForecastRequest(BaseModel):
    """Request model for forecast data queries."""

    parameter: str = Field(description="Parameter to forecast")

    msa: str = Field(description="Metropolitan Statistical Area code")

    horizon_years: int = Field(
        default=5, ge=1, le=10, description="Forecast horizon in years"
    )

    confidence_level: float = Field(
        default=0.95,
        ge=0.8,
        le=0.99,
        description="Confidence level for forecast intervals",
    )

    include_historical: bool = Field(
        default=True, description="Include historical data in response"
    )

    @validator("msa")
    def validate_msa(cls, v):
        """Validate MSA is supported."""
        supported_msas = ["NYC", "LA", "Chicago", "DC", "Miami"]
        if v not in supported_msas:
            raise ValueError(f"MSA must be one of: {supported_msas}")
        return v

    @validator("parameter")
    def validate_parameter(cls, v):
        """Validate parameter is supported."""
        supported_parameters = [
            "rent_growth_msa",
            "multifamily_cap_rate",
            "rental_vacancy_rate",
            "property_tax_growth",
            "maintenance_growth",
            "commercial_mortgage_rate",
            "treasury_10y",
        ]
        if v not in supported_parameters:
            raise ValueError(f"Parameter must be one of: {supported_parameters}")
        return v


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation analysis."""

    property_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique identifier for the property",
    )

    msa_code: str = Field(..., description="MSA (Metropolitan Statistical Area) code")

    num_scenarios: int = Field(
        default=10000,
        ge=500,
        le=50000,
        description="Number of Monte Carlo scenarios to generate",
    )

    horizon_years: int = Field(
        default=6, ge=3, le=10, description="Forecast horizon in years"
    )

    use_correlations: bool = Field(
        default=True, description="Use parameter correlations in simulation"
    )

    confidence_level: float = Field(
        default=0.95,
        ge=0.8,
        le=0.99,
        description="Confidence level for statistical analysis",
    )

    request_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional request identifier for tracking",
    )

    @validator("msa_code")
    def validate_msa_code(cls, v):
        """Validate MSA code is supported."""
        supported_msas = [
            "35620",
            "31080",
            "16980",
            "47900",
            "33100",
        ]  # NYC, LA, Chicago, DC, Miami
        if v not in supported_msas:
            raise ValueError(f"MSA code must be one of: {supported_msas}")
        return v
