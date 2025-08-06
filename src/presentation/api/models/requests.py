"""
API Request Models

Pydantic models for validating and serializing API request data.
"""

import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

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

    def __init__(self, **data):
        """Initialize with default options if not provided."""
        if "options" not in data or data["options"] is None:
            data["options"] = AnalysisOptions()
        super().__init__(**data)


class BatchAnalysisRequest(BaseModel):
    """Request model for batch property analysis."""

    properties: List[PropertyAnalysisRequest] = Field(
        description="List of properties to analyze", min_length=1, max_length=50
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

    @field_validator("properties")
    @classmethod
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

    @field_validator("percentiles")
    @classmethod
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

    @field_validator("msa")
    @classmethod
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

    @field_validator("msa")
    @classmethod
    def validate_msa(cls, v):
        """Validate MSA is supported."""
        supported_msas = ["NYC", "LA", "Chicago", "DC", "Miami"]
        if v not in supported_msas:
            raise ValueError(f"MSA must be one of: {supported_msas}")
        return v

    @field_validator("parameter")
    @classmethod
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
