"""
Custom Exceptions

Defines custom exception classes for the pro forma analytics tool
with standardized error handling, error codes, and contextual information.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """Standard error codes for pro forma analytics exceptions."""
    
    # Data-related errors (1000-1999)
    DATA_NOT_FOUND = "E1001"
    DATA_INCOMPLETE = "E1002"
    DATA_INVALID_FORMAT = "E1003"
    DATA_OUT_OF_RANGE = "E1004"
    
    # Database errors (2000-2999)
    DATABASE_CONNECTION_FAILED = "E2001"
    DATABASE_QUERY_FAILED = "E2002"
    DATABASE_TRANSACTION_FAILED = "E2003"
    DATABASE_INTEGRITY_ERROR = "E2004"
    
    # Validation errors (3000-3999)
    VALIDATION_FAILED = "E3001"
    PARAMETER_INVALID = "E3002"
    BUSINESS_RULE_VIOLATION = "E3003"
    DATE_RANGE_INVALID = "E3004"
    
    # Forecasting errors (4000-4999)
    FORECAST_MODEL_FAILED = "E4001"
    FORECAST_INSUFFICIENT_DATA = "E4002"
    FORECAST_CONVERGENCE_FAILED = "E4003"
    FORECAST_QUALITY_LOW = "E4004"
    
    # Monte Carlo errors (5000-5999)
    MONTE_CARLO_SETUP_FAILED = "E5001"
    MONTE_CARLO_EXECUTION_FAILED = "E5002"
    MONTE_CARLO_INSUFFICIENT_SCENARIOS = "E5003"
    MONTE_CARLO_CORRELATION_INVALID = "E5004"
    
    # Configuration errors (6000-6999)
    CONFIG_MISSING = "E6001"
    CONFIG_INVALID = "E6002"
    CONFIG_FILE_NOT_FOUND = "E6003"
    CONFIG_PERMISSION_DENIED = "E6004"
    
    # API errors (7000-7999)
    API_REQUEST_FAILED = "E7001"
    API_AUTHENTICATION_FAILED = "E7002"
    API_RATE_LIMIT_EXCEEDED = "E7003"
    API_DATA_UNAVAILABLE = "E7004"
    
    # Property data errors (8000-8999)
    PROPERTY_DATA_INVALID = "E8001"
    PROPERTY_NOT_FOUND = "E8002"
    PROPERTY_CALCULATION_FAILED = "E8003"
    PROPERTY_ANALYSIS_INCOMPLETE = "E8004"


class ProFormaAnalyticsError(Exception):
    """
    Base exception for pro forma analytics errors.
    
    Provides standardized error handling with error codes, context,
    and user-friendly messages.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Standardized error code
            context: Additional context information
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """Return formatted error message."""
        parts = []
        
        if self.error_code:
            parts.append(f"[{self.error_code.value}]")
        
        parts.append(self.message)
        
        if self.context:
            context_items = [f"{k}={v}" for k, v in self.context.items()]
            parts.append(f"Context: {', '.join(context_items)}")
        
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code.value if self.error_code else None,
            'context': self.context,
            'cause': str(self.cause) if self.cause else None
        }


class DataNotFoundError(ProFormaAnalyticsError):
    """Raised when required data is not found."""
    
    def __init__(
        self,
        message: str = "Required data not found",
        parameter_name: Optional[str] = None,
        geographic_code: Optional[str] = None,
        date_range: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if parameter_name:
            context['parameter_name'] = parameter_name
        if geographic_code:
            context['geographic_code'] = geographic_code
        if date_range:
            context['date_range'] = date_range
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DATA_NOT_FOUND,
            context=context,
            **kwargs
        )


class ForecastError(ProFormaAnalyticsError):
    """Raised when forecasting operations fail."""
    
    def __init__(
        self,
        message: str = "Forecasting operation failed",
        model_type: Optional[str] = None,
        parameter_name: Optional[str] = None,
        horizon_years: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if model_type:
            context['model_type'] = model_type
        if parameter_name:
            context['parameter_name'] = parameter_name
        if horizon_years:
            context['horizon_years'] = horizon_years
        
        super().__init__(
            message=message,
            error_code=ErrorCode.FORECAST_MODEL_FAILED,
            context=context,
            **kwargs
        )


class DatabaseError(ProFormaAnalyticsError):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        table_name: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if operation:
            context['operation'] = operation
        if table_name:
            context['table_name'] = table_name
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_QUERY_FAILED,
            context=context,
            **kwargs
        )


class ValidationError(ProFormaAnalyticsError):
    """Raised when data validation fails."""
    
    def __init__(
        self,
        message: str = "Data validation failed",
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = str(field_value)
        if expected_type:
            context['expected_type'] = expected_type
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_FAILED,
            context=context,
            **kwargs
        )


class ConfigurationError(ProFormaAnalyticsError):
    """Raised when configuration is invalid."""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if config_key:
            context['config_key'] = config_key
        if config_file:
            context['config_file'] = config_file
        
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFIG_INVALID,
            context=context,
            **kwargs
        )


class APIError(ProFormaAnalyticsError):
    """Raised when API operations fail."""
    
    def __init__(
        self,
        message: str = "API operation failed",
        api_endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if api_endpoint:
            context['api_endpoint'] = api_endpoint
        if status_code:
            context['status_code'] = status_code
        if response_data:
            context['response_data'] = response_data
        
        super().__init__(
            message=message,
            error_code=ErrorCode.API_REQUEST_FAILED,
            context=context,
            **kwargs
        )


class MonteCarloError(ProFormaAnalyticsError):
    """Raised when Monte Carlo simulation fails."""
    
    def __init__(
        self,
        message: str = "Monte Carlo simulation failed",
        num_scenarios: Optional[int] = None,
        simulation_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if num_scenarios:
            context['num_scenarios'] = num_scenarios
        if simulation_id:
            context['simulation_id'] = simulation_id
        
        super().__init__(
            message=message,
            error_code=ErrorCode.MONTE_CARLO_EXECUTION_FAILED,
            context=context,
            **kwargs
        )


class PropertyDataError(ProFormaAnalyticsError):
    """Raised when property-specific data is invalid."""
    
    def __init__(
        self,
        message: str = "Property data error",
        property_id: Optional[str] = None,
        property_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.pop('context', {})
        if property_id:
            context['property_id'] = property_id
        if property_type:
            context['property_type'] = property_type
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PROPERTY_DATA_INVALID,
            context=context,
            **kwargs
        )