"""
Domain Entities for Forecasting

Clean architecture implementation of core business entities.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid


class ParameterType(Enum):
    """Types of pro forma parameters."""
    INTEREST_RATE = "interest_rate"
    MARKET_METRIC = "market_metric"
    LENDING_REQUIREMENT = "lending_requirement"
    GROWTH_METRIC = "growth_metric"


class GeographicScope(Enum):
    """Geographic scope of parameters."""
    NATIONAL = "NATIONAL"
    MSA = "msa"
    STATE = "state"
    COUNTY = "county"


@dataclass(frozen=True)
class ParameterId:
    """Value object for parameter identification."""
    name: str
    geographic_code: str
    parameter_type: ParameterType
    
    def __post_init__(self):
        if not self.name or not self.geographic_code:
            raise ValueError("Parameter name and geographic code are required")


@dataclass(frozen=True)
class DataPoint:
    """Individual historical data point."""
    parameter_id: ParameterId
    date: date
    value: float
    data_source: str
    
    def __post_init__(self):
        if self.value is None:
            raise ValueError("Data point value cannot be None")


@dataclass(frozen=True)
class HistoricalData:
    """Collection of historical data points for a parameter."""
    parameter_id: ParameterId
    data_points: List[DataPoint]
    start_date: date
    end_date: date
    
    def __post_init__(self):
        if not self.data_points:
            raise ValueError("Historical data must contain at least one data point")
        
        # Validate date range consistency
        actual_start = min(dp.date for dp in self.data_points)
        actual_end = max(dp.date for dp in self.data_points)
        
        if actual_start != self.start_date or actual_end != self.end_date:
            raise ValueError("Date range does not match actual data points")
    
    @property
    def values(self) -> List[float]:
        """Extract values as a list."""
        return [dp.value for dp in sorted(self.data_points, key=lambda x: x.date)]
    
    @property
    def dates(self) -> List[date]:
        """Extract dates as a list."""
        return [dp.date for dp in sorted(self.data_points, key=lambda x: x.date)]


@dataclass(frozen=True)
class ForecastPoint:
    """Individual forecast data point."""
    date: date
    value: float
    lower_bound: float
    upper_bound: float


@dataclass(frozen=True)
class ModelPerformance:
    """Model performance metrics."""
    mae: float  # Mean Absolute Error
    mape: float  # Mean Absolute Percentage Error
    rmse: float  # Root Mean Square Error
    r_squared: float
    
    def is_acceptable(self, thresholds: Dict[str, float]) -> bool:
        """Check if performance meets acceptable thresholds."""
        return (
            self.mae <= thresholds.get('mae', float('inf')) and
            self.mape <= thresholds.get('mape', float('inf')) and
            self.rmse <= thresholds.get('rmse', float('inf')) and
            self.r_squared >= thresholds.get('r_squared', 0.0)
        )


@dataclass(frozen=True)
class ForecastResult:
    """Complete forecast result for a parameter."""
    forecast_id: str
    parameter_id: ParameterId
    forecast_points: List[ForecastPoint]
    model_performance: ModelPerformance
    model_type: str
    forecast_date: datetime
    horizon_years: int
    historical_data_points: int
    
    def __post_init__(self):
        if not self.forecast_points:
            raise ValueError("Forecast must contain at least one point")
        
        if self.horizon_years <= 0:
            raise ValueError("Forecast horizon must be positive")
            
        # Generate forecast_id if not provided
        if not self.forecast_id:
            object.__setattr__(self, 'forecast_id', str(uuid.uuid4()))
    
    @property
    def values(self) -> List[float]:
        """Extract forecast values as a list."""
        return [fp.value for fp in self.forecast_points]
    
    @property
    def dates(self) -> List[date]:
        """Extract forecast dates as a list."""
        return [fp.date for fp in self.forecast_points]
    
    @property
    def confidence_bounds(self) -> tuple[List[float], List[float]]:
        """Extract confidence bounds as tuple of (lower, upper) lists."""
        lower = [fp.lower_bound for fp in self.forecast_points]
        upper = [fp.upper_bound for fp in self.forecast_points]
        return lower, upper


@dataclass
class ForecastRequest:
    """Request for generating a forecast."""
    parameter_id: ParameterId
    horizon_years: int
    model_type: str = "prophet"
    confidence_level: float = 0.95
    
    def __post_init__(self):
        if self.horizon_years <= 0:
            raise ValueError("Forecast horizon must be positive")
        
        if not 0 < self.confidence_level < 1:
            raise ValueError("Confidence level must be between 0 and 1")