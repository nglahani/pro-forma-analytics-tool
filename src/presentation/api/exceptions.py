"""
FastAPI Exception Handlers

Custom exception handlers for mapping domain exceptions to HTTP responses.
"""

import sys
from pathlib import Path

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.exceptions import ConfigurationError
from core.exceptions import ValidationError as DomainValidationError
from core.logging_config import get_logger
from src.presentation.api.models.errors import (
    APIError,
    CalculationError,
    ErrorCode,
    ServiceError,
    ValidationError,
)

logger = get_logger(__name__)


async def domain_validation_error_handler(
    request: Request, exc: DomainValidationError
) -> JSONResponse:
    """
    Handle domain validation errors from business logic.

    Args:
        request: FastAPI request object
        exc: Domain validation error

    Returns:
        JSON response with validation error details
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"Domain validation error in request {request_id}: {exc}",
        extra={
            "structured_data": {
                "event": "domain_validation_error",
                "request_id": request_id,
                "path": request.url.path,
                "error_message": str(exc),
            }
        },
    )

    # Extract field-specific errors if available
    field_errors = {}
    invalid_fields = []

    if hasattr(exc, "field_errors"):
        field_errors = exc.field_errors
        invalid_fields = list(field_errors.keys())
    else:
        # Generic validation error
        field_errors = {"general": [str(exc)]}
        invalid_fields = ["general"]

    error = ValidationError(
        message=f"Validation failed: {exc}",
        field_errors=field_errors,
        invalid_fields=invalid_fields,
        request_id=request_id,
        path=request.url.path,
    )

    # Convert datetime for JSON serialization
    error_dict = error.model_dump(mode="json")
    if "timestamp" in error_dict:
        error_dict["timestamp"] = error.timestamp.isoformat()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_dict
    )


async def pydantic_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors from request parsing.

    Args:
        request: FastAPI request object
        exc: Pydantic validation error

    Returns:
        JSON response with field-specific validation errors
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        f"Request validation error in request {request_id}: {exc}",
        extra={
            "structured_data": {
                "event": "request_validation_error",
                "request_id": request_id,
                "path": request.url.path,
                "error_count": len(exc.errors()),
            }
        },
    )

    # Process Pydantic error details
    field_errors = {}
    invalid_fields = []

    for error_detail in exc.errors():
        field_path = ".".join(
            str(loc) for loc in error_detail["loc"][1:]
        )  # Skip 'body'
        if not field_path:
            field_path = "request"

        if field_path not in field_errors:
            field_errors[field_path] = []

        field_errors[field_path].append(error_detail["msg"])

        if field_path not in invalid_fields:
            invalid_fields.append(field_path)

    error = ValidationError(
        message="Request validation failed",
        field_errors=field_errors,
        invalid_fields=invalid_fields,
        request_id=request_id,
        path=request.url.path,
    )

    # Convert datetime for JSON serialization
    error_dict = error.model_dump(mode="json")
    if "timestamp" in error_dict:
        error_dict["timestamp"] = error.timestamp.isoformat()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_dict
    )


async def configuration_error_handler(
    request: Request, exc: ConfigurationError
) -> JSONResponse:
    """
    Handle configuration errors.

    Args:
        request: FastAPI request object
        exc: Configuration error

    Returns:
        JSON response with service error details
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"Configuration error in request {request_id}: {exc}",
        extra={
            "structured_data": {
                "event": "configuration_error",
                "request_id": request_id,
                "path": request.url.path,
                "error_message": str(exc),
            }
        },
    )

    error = ServiceError(
        message="Service configuration error",
        service_name="api_configuration",
        retry_recommended=False,
        details={"configuration_issue": str(exc)},
        request_id=request_id,
        path=request.url.path,
    )

    # Convert datetime for JSON serialization
    error_dict = error.model_dump(mode="json")
    if "timestamp" in error_dict:
        error_dict["timestamp"] = error.timestamp.isoformat()

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=error_dict
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.

    Args:
        request: FastAPI request object
        exc: HTTP exception

    Returns:
        JSON response with standardized error format
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # Map HTTP status codes to error types
    error_code_mapping = {
        400: ErrorCode.INVALID_INPUT,
        401: ErrorCode.AUTHENTICATION_FAILED,
        403: ErrorCode.AUTHORIZATION_FAILED,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }

    error_code = error_code_mapping.get(
        exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR
    )

    logger.warning(
        f"HTTP exception in request {request_id}: {exc.status_code} - {exc.detail}",
        extra={
            "structured_data": {
                "event": "http_exception",
                "request_id": request_id,
                "path": request.url.path,
                "status_code": exc.status_code,
                "detail": str(exc.detail),
            }
        },
    )

    error = APIError(
        error_code=error_code,
        message=str(exc.detail),
        details={"http_status": exc.status_code},
        request_id=request_id,
        path=request.url.path,
    )

    # Convert datetime for JSON serialization
    error_dict = error.model_dump(mode="json")
    if "timestamp" in error_dict:
        error_dict["timestamp"] = error.timestamp.isoformat()

    return JSONResponse(status_code=exc.status_code, content=error_dict)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request object
        exc: Unexpected exception

    Returns:
        JSON response with generic error information
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"Unexpected exception in request {request_id}: {type(exc).__name__}: {exc}",
        extra={
            "structured_data": {
                "event": "unexpected_exception",
                "request_id": request_id,
                "path": request.url.path,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }
        },
        exc_info=True,
    )

    error = ServiceError(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred",
        service_name="api_server",
        retry_recommended=True,
        details={"exception_type": type(exc).__name__},
        request_id=request_id,
        path=request.url.path,
    )

    # Convert datetime for JSON serialization
    error_dict = error.model_dump(mode="json")
    if "timestamp" in error_dict:
        error_dict["timestamp"] = error.timestamp.isoformat()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_dict
    )


# DCF-specific exception handlers
async def calculation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle DCF calculation errors.

    Args:
        request: FastAPI request object
        exc: Calculation error

    Returns:
        JSON response with calculation error details
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        f"DCF calculation error in request {request_id}: {exc}",
        extra={
            "structured_data": {
                "event": "dcf_calculation_error",
                "request_id": request_id,
                "path": request.url.path,
                "error_message": str(exc),
            }
        },
    )

    error = CalculationError(
        message=f"DCF calculation failed: {exc}",
        calculation_phase="unknown",
        suggested_fixes=["Check input parameters", "Verify data ranges"],
        request_id=request_id,
        path=request.url.path,
    )

    # Convert datetime for JSON serialization
    error_dict = error.model_dump(mode="json")
    if "timestamp" in error_dict:
        error_dict["timestamp"] = error.timestamp.isoformat()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_dict
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Domain-specific exception handlers
    app.add_exception_handler(DomainValidationError, domain_validation_error_handler)
    app.add_exception_handler(ConfigurationError, configuration_error_handler)

    # FastAPI built-in exception handlers
    app.add_exception_handler(RequestValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Generic exception handler (catches all other exceptions)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")
