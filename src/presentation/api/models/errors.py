"""
API Error Models

Pydantic models for structured error responses.
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Standard error codes for API responses."""

    # Client errors (4xx)
    INVALID_INPUT = "invalid_input"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    REQUEST_TIMEOUT = "request_timeout"

    # Business logic errors
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    INSUFFICIENT_DATA = "insufficient_data"
    CALCULATION_ERROR = "calculation_error"

    # Server errors (5xx)
    INTERNAL_SERVER_ERROR = "internal_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DATABASE_ERROR = "database_error"
    EXTERNAL_API_ERROR = "external_api_error"


class APIError(BaseModel):
    """Base error response model."""

    error_code: ErrorCode = Field(description="Machine-readable error classification")

    message: str = Field(description="Human-readable error message")

    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error context and information"
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When the error occurred"
    )

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    request_id: Optional[str] = Field(
        default=None, description="Request identifier for error correlation"
    )

    path: Optional[str] = Field(
        default=None, description="API endpoint where error occurred"
    )


class ValidationError(APIError):
    """Validation error with field-specific details."""

    error_code: ErrorCode = Field(
        default=ErrorCode.VALIDATION_ERROR,
        description="Always validation_error for this type",
    )

    field_errors: Dict[str, List[str]] = Field(
        description="Field-specific validation error messages"
    )

    invalid_fields: List[str] = Field(
        description="List of fields that failed validation"
    )


class BusinessLogicError(APIError):
    """Business rule violation error."""

    error_code: ErrorCode = Field(
        default=ErrorCode.BUSINESS_RULE_VIOLATION,
        description="Business rule violation classification",
    )

    business_rule: str = Field(description="The business rule that was violated")

    suggested_action: Optional[str] = Field(
        default=None, description="Suggested action to resolve the error"
    )

    rule_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Context information about the rule violation"
    )


class AuthenticationError(APIError):
    """Authentication failure error."""

    error_code: ErrorCode = Field(
        default=ErrorCode.AUTHENTICATION_FAILED,
        description="Authentication failure classification",
    )

    auth_method: Optional[str] = Field(
        default=None, description="Authentication method that failed"
    )

    required_permissions: Optional[List[str]] = Field(
        default=None, description="Permissions required for the operation"
    )


class RateLimitError(APIError):
    """Rate limit exceeded error."""

    error_code: ErrorCode = Field(
        default=ErrorCode.RATE_LIMIT_EXCEEDED,
        description="Rate limit exceeded classification",
    )

    limit: int = Field(description="Rate limit threshold")

    window_seconds: int = Field(description="Rate limit window in seconds")

    retry_after_seconds: int = Field(description="Seconds to wait before retrying")

    current_usage: Optional[int] = Field(
        default=None, description="Current usage count within window"
    )


class ServiceError(APIError):
    """Service unavailable or internal error."""

    error_code: ErrorCode = Field(
        default=ErrorCode.SERVICE_UNAVAILABLE,
        description="Service error classification",
    )

    service_name: Optional[str] = Field(
        default=None, description="Name of the affected service"
    )

    retry_recommended: bool = Field(
        default=False, description="Whether retrying the request is recommended"
    )

    estimated_recovery_time: Optional[int] = Field(
        default=None, description="Estimated recovery time in seconds"
    )


class CalculationError(APIError):
    """DCF calculation or analysis error."""

    error_code: ErrorCode = Field(
        default=ErrorCode.CALCULATION_ERROR,
        description="Calculation error classification",
    )

    calculation_phase: Optional[str] = Field(
        default=None, description="DCF phase where error occurred"
    )

    parameter_issues: Optional[List[str]] = Field(
        default=None, description="Parameters that caused calculation issues"
    )

    suggested_fixes: Optional[List[str]] = Field(
        default=None, description="Suggested parameter adjustments"
    )


class DataError(APIError):
    """Data availability or quality error."""

    error_code: ErrorCode = Field(
        default=ErrorCode.INSUFFICIENT_DATA, description="Data error classification"
    )

    missing_data: Optional[List[str]] = Field(
        default=None, description="List of missing data elements"
    )

    data_quality_issues: Optional[List[str]] = Field(
        default=None, description="Identified data quality problems"
    )

    alternative_approaches: Optional[List[str]] = Field(
        default=None, description="Alternative analysis approaches"
    )
