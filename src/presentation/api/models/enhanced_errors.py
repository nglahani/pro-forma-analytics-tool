"""
Enhanced Error Response Models

Comprehensive error response structures with actionable suggestions and debugging information.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EnhancedErrorResponse(BaseModel):
    """Base enhanced error response model with comprehensive debugging information."""

    error_code: str = Field(
        ..., description="Programmatic error code for client handling"
    )
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details and context"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Actionable suggestions to resolve the error"
    )
    documentation_url: Optional[str] = Field(
        None, description="Link to relevant documentation section"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error occurrence timestamp in UTC"
    )
    request_id: str = Field(..., description="Unique request identifier for debugging")
    path: str = Field(..., description="API endpoint path where error occurred")

    class Config:
        schema_extra = {
            "example": {
                "error_code": "validation_error",
                "message": "Invalid property data provided",
                "details": {"http_status": 422},
                "suggestions": [
                    "Check required fields are provided",
                    "Verify data types match API specification",
                ],
                "documentation_url": "http://localhost:8000/api/v1/docs#/analysis/dcf_analysis",
                "timestamp": "2025-07-31T18:50:00Z",
                "request_id": "req_1753998250000_validation_error",
                "path": "/api/v1/analysis/dcf",
            }
        }


class ValidationErrorResponse(EnhancedErrorResponse):
    """Enhanced validation error response with field-specific details."""

    field_errors: Dict[str, List[str]] = Field(
        default_factory=dict, description="Field-specific validation error messages"
    )
    invalid_fields: List[str] = Field(
        default_factory=list, description="List of fields that failed validation"
    )
    example_valid_request: Optional[Dict[str, Any]] = Field(
        None, description="Example of valid request structure"
    )

    class Config:
        schema_extra = {
            "example": {
                "error_code": "validation_error",
                "message": "Property data validation failed",
                "details": {"http_status": 422},
                "field_errors": {
                    "property_data.residential_units.total_units": [
                        "Total units must be greater than 0"
                    ],
                    "property_data.purchase_price": [
                        "Purchase price must be a positive number"
                    ],
                },
                "invalid_fields": [
                    "property_data.residential_units.total_units",
                    "property_data.purchase_price",
                ],
                "suggestions": [
                    "Ensure all required fields are provided",
                    "Verify numeric fields contain positive values",
                    "Check field names match API specification exactly",
                ],
                "documentation_url": "http://localhost:8000/api/v1/docs#/analysis/dcf_analysis",
                "timestamp": "2025-07-31T18:50:00Z",
                "request_id": "req_validation_001",
                "path": "/api/v1/analysis/dcf",
            }
        }


class AuthenticationErrorResponse(EnhancedErrorResponse):
    """Enhanced authentication error response with specific auth guidance."""

    auth_method: str = Field(
        default="API-Key", description="Expected authentication method"
    )
    missing_headers: List[str] = Field(
        default_factory=list, description="Required headers that are missing"
    )

    class Config:
        schema_extra = {
            "example": {
                "error_code": "authentication_failed",
                "message": "API key required for access",
                "details": {"http_status": 401, "auth_method": "API-Key"},
                "auth_method": "API-Key",
                "missing_headers": ["X-API-Key"],
                "suggestions": [
                    "Include X-API-Key header in your request",
                    "Verify API key is valid and active",
                    "Check API key has sufficient permissions for this endpoint",
                    "Contact support if you need a new API key",
                ],
                "documentation_url": "http://localhost:8000/api/v1/docs#section/Authentication",
                "timestamp": "2025-07-31T18:52:00Z",
                "request_id": "req_auth_001",
                "path": "/api/v1/analysis/dcf",
            }
        }


class CalculationErrorResponse(EnhancedErrorResponse):
    """Enhanced calculation error response with phase and parameter details."""

    calculation_phase: str = Field(
        ..., description="DCF calculation phase where error occurred"
    )
    parameter_issues: List[str] = Field(
        default_factory=list,
        description="Parameters or data sources that caused the error",
    )

    class Config:
        schema_extra = {
            "example": {
                "error_code": "calculation_error",
                "message": "Monte Carlo simulation failed: Expected 11 forecasts, found 0 for MSA 35620",
                "details": {
                    "http_status": 500,
                    "calculation_phase": "monte_carlo_simulation",
                },
                "calculation_phase": "monte_carlo_simulation",
                "parameter_issues": ["simulation_parameters", "forecasting_data"],
                "suggestions": [
                    "Verify property data values are realistic",
                    "Check MSA code is supported (35620, 31080, 16980, 47900, 33100)",
                    "Ensure all required financial parameters are provided",
                    "Reduce number of Monte Carlo scenarios if performance issues",
                    "Try a different forecast horizon (3-10 years)",
                ],
                "documentation_url": "http://localhost:8000/api/v1/docs#/simulation/monte_carlo_simulation",
                "timestamp": "2025-07-31T18:55:00Z",
                "request_id": "req_calc_001",
                "path": "/api/v1/simulation/monte-carlo",
            }
        }


class RateLimitErrorResponse(EnhancedErrorResponse):
    """Enhanced rate limit error response with retry guidance."""

    limit: int = Field(..., description="Rate limit threshold (requests per window)")
    window_seconds: int = Field(
        ..., description="Rate limit window duration in seconds"
    )
    current_usage: int = Field(..., description="Current request count in window")
    retry_after_seconds: int = Field(
        ..., description="Recommended wait time before retry"
    )

    class Config:
        schema_extra = {
            "example": {
                "error_code": "rate_limit_exceeded",
                "message": "Too many requests. Rate limit exceeded.",
                "details": {
                    "http_status": 429,
                    "limit": 100,
                    "window_seconds": 60,
                    "current_usage": 101,
                },
                "limit": 100,
                "window_seconds": 60,
                "current_usage": 101,
                "retry_after_seconds": 45,
                "suggestions": [
                    "Wait 45 seconds before making additional requests",
                    "Implement exponential backoff in your client",
                    "Consider upgrading to higher rate limit tier",
                    "Use batch endpoints for multiple properties to optimize usage",
                    "Cache frequently requested market data locally",
                ],
                "documentation_url": "http://localhost:8000/api/v1/docs#section/Rate-Limiting",
                "timestamp": "2025-07-31T18:58:00Z",
                "request_id": "req_rate_limit_001",
                "path": "/api/v1/analysis/dcf",
            }
        }


class DataErrorResponse(EnhancedErrorResponse):
    """Enhanced data error response for missing or invalid data sources."""

    missing_data_sources: List[str] = Field(
        default_factory=list, description="Data sources that are missing or unavailable"
    )
    data_quality_issues: List[str] = Field(
        default_factory=list, description="Specific data quality problems identified"
    )
    affected_parameters: List[str] = Field(
        default_factory=list, description="Pro forma parameters affected by data issues"
    )

    class Config:
        schema_extra = {
            "example": {
                "error_code": "data_unavailable",
                "message": "Required market data not available for MSA 99999",
                "details": {"http_status": 400, "data_coverage": "unsupported_msa"},
                "missing_data_sources": [
                    "historical_cap_rates",
                    "rent_growth_forecasts",
                    "property_appreciation_data",
                ],
                "data_quality_issues": [
                    "MSA code not in supported list",
                    "Insufficient historical data points",
                ],
                "affected_parameters": ["cap_rate", "rent_growth", "property_growth"],
                "suggestions": [
                    "Use supported MSA codes: 35620 (NYC), 31080 (LA), 16980 (Chicago), 47900 (DC), 33100 (Miami)",
                    "Verify MSA code matches property location",
                    "Contact support to request additional MSA coverage",
                    "Use nearby supported MSA as proxy for analysis",
                ],
                "documentation_url": "http://localhost:8000/api/v1/docs#section/Supported-Markets",
                "timestamp": "2025-07-31T19:00:00Z",
                "request_id": "req_data_001",
                "path": "/api/v1/analysis/dcf",
            }
        }


class InternalServerErrorResponse(EnhancedErrorResponse):
    """Enhanced internal server error response with debugging information."""

    error_id: str = Field(..., description="Internal error tracking identifier")
    service_status: Dict[str, str] = Field(
        default_factory=dict, description="Status of internal services"
    )

    class Config:
        schema_extra = {
            "example": {
                "error_code": "internal_server_error",
                "message": "An unexpected error occurred while processing your request",
                "details": {"http_status": 500, "error_category": "system_error"},
                "error_id": "err_internal_001_abc123",
                "service_status": {
                    "database": "healthy",
                    "forecasting_engine": "degraded",
                    "monte_carlo_engine": "healthy",
                },
                "suggestions": [
                    "Retry your request in a few moments",
                    "If problem persists, contact support with error ID: err_internal_001_abc123",
                    "Check system status page for known issues",
                    "Reduce request complexity if possible (fewer scenarios, shorter horizon)",
                ],
                "documentation_url": "http://localhost:8000/api/v1/docs#section/Error-Handling",
                "timestamp": "2025-07-31T19:05:00Z",
                "request_id": "req_internal_001",
                "path": "/api/v1/analysis/dcf",
            }
        }


# Error suggestion mappings for programmatic use
ERROR_SUGGESTIONS = {
    "validation_error": [
        "Check required fields are provided",
        "Verify data types match API specification",
        "Review field validation rules in documentation",
        "Ensure numeric fields contain positive values where required",
    ],
    "authentication_failed": [
        "Ensure X-API-Key header is included",
        "Verify API key is valid and active",
        "Check API key has sufficient permissions",
        "Contact support if you need a new API key",
    ],
    "calculation_error": [
        "Verify property data values are realistic",
        "Check MSA code is supported (35620, 31080, 16980, 47900, 33100)",
        "Ensure all required financial parameters are provided",
        "Reduce number of Monte Carlo scenarios if performance issues",
        "Try a different forecast horizon (3-10 years)",
    ],
    "rate_limit_exceeded": [
        "Wait before making additional requests",
        "Implement exponential backoff in your client",
        "Consider upgrading to higher rate limit tier",
        "Use batch endpoints for multiple properties",
        "Cache frequently requested data locally",
    ],
    "data_unavailable": [
        "Use supported MSA codes: 35620, 31080, 16980, 47900, 33100",
        "Verify MSA code matches property location",
        "Contact support to request additional MSA coverage",
        "Use nearby supported MSA as proxy",
    ],
    "internal_server_error": [
        "Retry your request in a few moments",
        "Contact support if problem persists",
        "Check system status page for known issues",
        "Reduce request complexity if possible",
    ],
}

# Documentation URL patterns
DOCUMENTATION_URLS = {
    "dcf_analysis": "http://localhost:8000/api/v1/docs#/analysis/dcf_analysis",
    "batch_analysis": "http://localhost:8000/api/v1/docs#/analysis/batch_analysis",
    "monte_carlo": "http://localhost:8000/api/v1/docs#/simulation/monte_carlo_simulation",
    "market_data": "http://localhost:8000/api/v1/docs#/data/market_data",
    "authentication": "http://localhost:8000/api/v1/docs#section/Authentication",
    "rate_limiting": "http://localhost:8000/api/v1/docs#section/Rate-Limiting",
    "supported_markets": "http://localhost:8000/api/v1/docs#section/Supported-Markets",
    "error_handling": "http://localhost:8000/api/v1/docs#section/Error-Handling",
}


def get_error_suggestions(error_code: str) -> List[str]:
    """Get predefined suggestions for an error code."""
    return ERROR_SUGGESTIONS.get(
        error_code,
        [
            "Review the error message for specific guidance",
            "Check API documentation for endpoint requirements",
            "Contact support if you need assistance",
        ],
    )


def get_documentation_url(endpoint_type: str) -> str:
    """Get documentation URL for an endpoint type."""
    return DOCUMENTATION_URLS.get(endpoint_type, "http://localhost:8000/api/v1/docs")


def create_validation_error(
    message: str,
    field_errors: Dict[str, List[str]],
    request_id: str,
    path: str,
    example_request: Optional[Dict[str, Any]] = None,
) -> ValidationErrorResponse:
    """Create a standardized validation error response."""
    return ValidationErrorResponse(
        error_code="validation_error",
        message=message,
        details={"http_status": 422},
        field_errors=field_errors,
        invalid_fields=list(field_errors.keys()),
        suggestions=get_error_suggestions("validation_error"),
        documentation_url=get_documentation_url("dcf_analysis"),
        request_id=request_id,
        path=path,
        example_valid_request=example_request,
    )


def create_calculation_error(
    message: str,
    calculation_phase: str,
    parameter_issues: List[str],
    request_id: str,
    path: str,
) -> CalculationErrorResponse:
    """Create a standardized calculation error response."""
    return CalculationErrorResponse(
        error_code="calculation_error",
        message=message,
        details={"http_status": 500, "calculation_phase": calculation_phase},
        calculation_phase=calculation_phase,
        parameter_issues=parameter_issues,
        suggestions=get_error_suggestions("calculation_error"),
        documentation_url=get_documentation_url("monte_carlo"),
        request_id=request_id,
        path=path,
    )


def create_authentication_error(
    message: str, missing_headers: List[str], request_id: str, path: str
) -> AuthenticationErrorResponse:
    """Create a standardized authentication error response."""
    return AuthenticationErrorResponse(
        error_code="authentication_failed",
        message=message,
        details={"http_status": 401, "auth_method": "API-Key"},
        missing_headers=missing_headers,
        suggestions=get_error_suggestions("authentication_failed"),
        documentation_url=get_documentation_url("authentication"),
        request_id=request_id,
        path=path,
    )
