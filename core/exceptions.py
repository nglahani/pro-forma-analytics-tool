"""
Custom Exceptions

Defines custom exception classes for the pro forma analytics tool.
"""


class ProFormaAnalyticsError(Exception):
    """Base exception for pro forma analytics errors."""
    pass


class DataNotFoundError(ProFormaAnalyticsError):
    """Raised when required data is not found."""
    pass


class ForecastError(ProFormaAnalyticsError):
    """Raised when forecasting operations fail."""
    pass


class DatabaseError(ProFormaAnalyticsError):
    """Raised when database operations fail."""
    pass


class ValidationError(ProFormaAnalyticsError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(ProFormaAnalyticsError):
    """Raised when configuration is invalid."""
    pass


class APIError(ProFormaAnalyticsError):
    """Raised when API operations fail."""
    pass


class MonteCarloError(ProFormaAnalyticsError):
    """Raised when Monte Carlo simulation fails."""
    pass




class PropertyDataError(ProFormaAnalyticsError):
    """Raised when property-specific data is invalid."""
    pass