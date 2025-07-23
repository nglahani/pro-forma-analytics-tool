"""
Repository Interfaces for Parameter Data

Abstracts data access for historical parameter data and forecasts.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Dict, Any

from ..entities.forecast import (
    ParameterId, 
    HistoricalData, 
    ForecastResult,
    DataPoint
)


class ParameterRepository(ABC):
    """Abstract repository for parameter data operations."""
    
    @abstractmethod
    def get_historical_data(
        self, 
        parameter_id: ParameterId,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Optional[HistoricalData]:
        """
        Retrieve historical data for a parameter.
        
        Args:
            parameter_id: Parameter identifier
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            HistoricalData if found, None otherwise
        """
        pass
    
    @abstractmethod
    def save_historical_data(self, historical_data: HistoricalData) -> None:
        """
        Save historical data for a parameter.
        
        Args:
            historical_data: Historical data to save
        """
        pass
    
    @abstractmethod
    def get_available_parameters(self, geographic_code: str) -> List[ParameterId]:
        """
        Get all available parameters for a geographic area.
        
        Args:
            geographic_code: Geographic identifier
            
        Returns:
            List of available parameter IDs
        """
        pass
    
    @abstractmethod
    def get_data_completeness(
        self, 
        parameter_id: ParameterId,
        start_date: date,
        end_date: date
    ) -> float:
        """
        Calculate data completeness percentage for a parameter.
        
        Args:
            parameter_id: Parameter identifier
            start_date: Start date for completeness check
            end_date: End date for completeness check
            
        Returns:
            Completeness percentage (0.0 to 1.0)
        """
        pass


class ForecastRepository(ABC):
    """Abstract repository for forecast data operations."""
    
    @abstractmethod
    def save_forecast(self, forecast_result: ForecastResult) -> None:
        """
        Save a forecast result.
        
        Args:
            forecast_result: Forecast result to save
        """
        pass
    
    @abstractmethod
    def get_cached_forecast(
        self,
        parameter_id: ParameterId,
        horizon_years: int,
        model_type: str,
        max_age_days: int = 30
    ) -> Optional[ForecastResult]:
        """
        Retrieve a cached forecast if available and not too old.
        
        Args:
            parameter_id: Parameter identifier
            horizon_years: Forecast horizon
            model_type: Type of forecasting model
            max_age_days: Maximum age in days for cached forecast
            
        Returns:
            ForecastResult if found and recent enough, None otherwise
        """
        pass
    
    @abstractmethod
    def get_forecasts_for_simulation(
        self,
        parameter_ids: List[ParameterId],
        horizon_years: int,
        model_type: str,
        max_age_days: int = 30
    ) -> Dict[ParameterId, ForecastResult]:
        """
        Get multiple forecasts for Monte Carlo simulation.
        
        Args:
            parameter_ids: List of parameter identifiers
            horizon_years: Forecast horizon
            model_type: Type of forecasting model
            max_age_days: Maximum age in days for cached forecasts
            
        Returns:
            Dictionary mapping parameter IDs to forecast results
        """
        pass
    
    @abstractmethod
    def delete_old_forecasts(self, older_than_days: int) -> int:
        """
        Delete forecasts older than specified days.
        
        Args:
            older_than_days: Delete forecasts older than this many days
            
        Returns:
            Number of forecasts deleted
        """
        pass


class CorrelationRepository(ABC):
    """Abstract repository for parameter correlation data."""
    
    @abstractmethod
    def save_correlation_matrix(
        self,
        geographic_code: str,
        correlation_matrix: List[List[float]],
        parameter_names: List[str],
        calculation_date: date,
        window_years: int
    ) -> None:
        """
        Save a parameter correlation matrix.
        
        Args:
            geographic_code: Geographic identifier
            correlation_matrix: Correlation matrix data
            parameter_names: Names of parameters in matrix order
            calculation_date: When the matrix was calculated
            window_years: Years of data used for calculation
        """
        pass
    
    @abstractmethod
    def get_correlation_matrix(
        self,
        geographic_code: str,
        parameter_names: List[str],
        max_age_days: int = 90
    ) -> Optional[tuple[List[List[float]], List[str], date]]:
        """
        Retrieve a correlation matrix if available and recent.
        
        Args:
            geographic_code: Geographic identifier
            parameter_names: Required parameter names
            max_age_days: Maximum age in days for cached matrix
            
        Returns:
            Tuple of (matrix, parameter_names, calculation_date) if found, None otherwise
        """
        pass